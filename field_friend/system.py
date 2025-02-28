import logging
import os
from typing import Dict, List, Optional, Union

import numpy as np
import rosys

from field_friend.automations import (BatteryWatcher, CoinCollecting, DemoWeeding, FieldProvider, Mowing, PathProvider,
                                      PathRecorder, PlantLocator, PlantProvider, Puncher, Weeding, WeedingNew)
from field_friend.hardware import FieldFriendHardware, FieldFriendSimulation
from field_friend.navigation import GnssHardware, GnssSimulation
from field_friend.vision import CameraConfigurator, SimulatedCam, SimulatedCamProvider, UsbCamProvider


class System:
    def __init__(self) -> None:
        rosys.hardware.SerialCommunication.search_paths.insert(0, '/dev/ttyTHS0')
        self.log = logging.getLogger('field_friend.system')
        self.is_real = rosys.hardware.SerialCommunication.is_possible()
        version = 'u4'  # insert here your field friend version
        if self.is_real:
            self.field_friend = FieldFriendHardware(version=version)
            self.usb_camera_provider = UsbCamProvider()
            self.detector = rosys.vision.DetectorHardware(port=8004)
            # self.circle_sight = CircleSight()
        else:
            self.field_friend = FieldFriendSimulation(version=version)
            self.usb_camera_provider = SimulatedCamProvider()
            self.usb_camera_provider.remove_all_cameras()
            self.usb_camera_provider.add_camera(SimulatedCam.create_calibrated(id='bottom_cam',
                                                                               x=0.4, z=0.4,
                                                                               roll=np.deg2rad(360-150),
                                                                               pitch=np.deg2rad(0),
                                                                               yaw=np.deg2rad(90)))
            self.detector = rosys.vision.DetectorSimulation(self.usb_camera_provider)
            # self.circle_sight = None
        self.camera_configurator = CameraConfigurator(self.usb_camera_provider, version)
        self.plant_provider = PlantProvider()
        self.field_provider = FieldProvider()
        self.steerer = rosys.driving.Steerer(self.field_friend.wheels, speed_scaling=0.25)
        self.odometer = rosys.driving.Odometer(self.field_friend.wheels)
        if self.is_real:
            self.gnss = GnssHardware(self.odometer)
        else:
            self.gnss = GnssSimulation(self.field_friend.wheels)
        self.gnss.ROBOT_POSE_LOCATED.register(self.forward_pose_odometer)
        self.driver = rosys.driving.Driver(self.field_friend.wheels, self.odometer)
        self.driver.parameters.linear_speed_limit = 0.1
        self.driver.parameters.angular_speed_limit = 1.0
        self.driver.parameters.can_drive_backwards = False
        self.driver.parameters.minimum_turning_radius = 0.1
        self.driver.parameters.hook_offset = 0.6
        self.driver.parameters.carrot_distance = 0.2
        self.driver.parameters.carrot_offset = self.driver.parameters.hook_offset + self.driver.parameters.carrot_distance
        self.puncher = Puncher(self.field_friend, self.driver)
        self.big_weed_category_names = ['thistle', 'big_weed', 'orache']
        self.small_weed_category_names = ['weed', 'coin']
        self.crop_category_names = ['sugar_beet', 'crop', 'coin_with_hole']
        self.plant_locator = PlantLocator(self.usb_camera_provider, self.detector, self.plant_provider, self.odometer)
        self.plant_locator.weed_category_names = self.big_weed_category_names + self.small_weed_category_names
        self.plant_locator.crop_category_names = self.crop_category_names

        self.demo_weeding = DemoWeeding(self.field_friend, self.driver, self.detector,
                                        self.plant_provider, self.puncher, self.plant_locator)
        self.weeding = Weeding(self)
        self.weeding_new = WeedingNew(self)
        self.coin_collecting = CoinCollecting(self)
        self.path_provider = PathProvider()
        self.path_recorder = PathRecorder(self.path_provider, self.driver, self.steerer, self.gnss)
        self.field_provider = FieldProvider()

        width = 0.64
        length = 0.78
        offset = 0.36
        height = 0.67
        self.shape = rosys.geometry.Prism(
            outline=[
                (-offset, -width/2),
                (length - offset, -width/2),
                (length - offset, width/2),
                (-offset, width/2)
            ],
            height=height)
        self.path_planner = rosys.pathplanning.PathPlanner(self.shape)
        self.mowing = Mowing(self.field_friend, self.field_provider, driver=self.driver,
                             path_planner=self.path_planner, gnss=self.gnss, robot_width=width)

        self.automations = {'demo_weeding': self.demo_weeding.start,
                            'mowing': self.mowing.start,
                            'collecting': self.coin_collecting.start,
                            'weeding': self.weeding.start,
                            'weeding_new': self.weeding_new.start
                            }
        self.automator = rosys.automation.Automator(None, on_interrupt=self.field_friend.stop,
                                                    default_automation=self.coin_collecting.start)
        if self.is_real and self.field_friend.battery_control:
            self.battery_watcher = BatteryWatcher(self.field_friend, self.automator)

        async def stop():
            if self.automator.is_running:
                if self.field_friend.estop.is_soft_estop_active:
                    self.automator.pause(because='soft estop active')
                else:
                    self.automator.pause(because='emergency stop triggered')
            await self.field_friend.stop()

        def pause():
            if self.automator.is_running:
                if self.path_recorder.state != 'recording':
                    self.automator.pause(because='steering started')

        self.steerer.STEERING_STARTED.register(pause)
        self.field_friend.estop.ESTOP_TRIGGERED.register(stop)

    def forward_pose_odometer(self, pose: rosys.geometry.Pose) -> None:
        self.odometer.handle_detection(pose)

    def restart(self) -> None:
        os.utime('main.py')
