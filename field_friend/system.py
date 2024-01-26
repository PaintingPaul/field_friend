import logging
import os
from typing import Optional

import numpy as np
import rosys

from field_friend.automations import (CoinCollecting, DemoWeeding, FieldProvider, Mowing, PathProvider, PathRecorder,
                                      PlantLocator, PlantProvider, Puncher, Weeding, WeedingNew, Rolling)
from field_friend.hardware import FieldFriendHardware, FieldFriendSimulation
from field_friend.navigation import GnssHardware, GnssSimulation
from field_friend.vision import SimulatedCam, SimulatedCamProvider, UsbCamProvider
from field_friend.falling_detection import FallingSimulation


class System:
    def __init__(self) -> None:
        rosys.hardware.SerialCommunication.search_paths.insert(0, '/dev/ttyTHS0')
        self.log = logging.getLogger('field_friend.system')
        self.is_real = rosys.hardware.SerialCommunication.is_possible()
        version = 'u1'  # insert here your field friend version
        if self.is_real:
            self.field_friend = FieldFriendHardware(version=version)
            self.usb_camera_provider = UsbCamProvider()
            self.detector = rosys.vision.DetectorHardware(port=8004)
            # self.circle_sight = CircleSight()
        else:
            self.field_friend = FieldFriendSimulation(version=version)
            self.usb_camera_provider = SimulatedCamProvider()
            self.falling_detection = FallingSimulation(self.field_friend)
            self.usb_camera_provider.remove_all_cameras()
            self.usb_camera_provider.add_camera(SimulatedCam.create_calibrated(id='bottom_cam',
                                                                               x=0.4, z=0.4,
                                                                               roll=np.deg2rad(360-150),
                                                                               pitch=np.deg2rad(0),
                                                                               yaw=np.deg2rad(90)))
            self.detector = rosys.vision.DetectorSimulation(self.usb_camera_provider)
            # self.circle_sight = None
        self.plant_provider = PlantProvider()
        self.field_provider = FieldProvider()
        self.rolling = Rolling(self.field_friend.imu,self.field_friend)
        self.steerer = rosys.driving.Steerer(self.field_friend.wheels, speed_scaling=0.25)
        self.odometer = rosys.driving.Odometer(self.field_friend.wheels)
        if self.is_real:
            self.gnss = GnssHardware(self.odometer)
        else:
            self.gnss = GnssSimulation(self.field_friend.wheels)
        self.gnss.ROBOT_LOCATED.register(self.odometer.handle_detection)
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
        self.plant_locator: Optional[PlantLocator] = None
        # self.usb_camera_provider.CAMERA_ADDED.register(self._create_plant_locator)
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

        if self.is_real:
            # camera configuration
            def configure_cameras() -> None:
                for camera in self.usb_camera_provider.cameras.values():
                    if self.field_friend.version == 'ff3':
                        width, height, xoffset, yoffset = 1920, 1080, 420, 150
                        camera.resolution = rosys.vision.ImageSize(width=width, height=height)
                        camera.crop = rosys.geometry.Rectangle(
                            x=xoffset, y=0, width=width - (2 * xoffset + 150),
                            height=height - yoffset)
                        camera.auto_exposure = True
                    elif self.field_friend.version in ['u2', 'u1']:
                        width, height, xoffset, yoffset = 1920, 1080, 450, 30
                        camera.resolution = rosys.vision.ImageSize(width=width, height=height)
                        camera.crop = rosys.geometry.Rectangle(
                            x=xoffset, y=yoffset, width=width - 2 * xoffset, height=height - 2 * yoffset)
                        camera.auto_exposure = True
                        # camera.exposure = 0.005
                    elif self.field_friend.version in ['u3']:
                        width, height, xoffset, yoffset, width_offset = 1920, 1080, 400, 100, 200
                        camera.resolution = rosys.vision.ImageSize(width=width, height=height)
                        camera.crop = rosys.geometry.Rectangle(
                            x=xoffset, y=yoffset, width=width - 2 * xoffset - width_offset, height=height - 2 * yoffset)
                        camera.rotation = 90
                        camera.auto_exposure = False
                        camera.exposure = 0.004
                    elif self.field_friend.version in ['u4']:
                        width, height, xoffset, yoffset = 1920, 1080, 350, 50
                        camera.resolution = rosys.vision.ImageSize(width=width, height=height)
                        camera.crop = rosys.geometry.Rectangle(
                            x=xoffset, y=yoffset, width=width - 2 * xoffset, height=height - 2 * yoffset)
                        camera.rotation = 0
                        camera.auto_exposure = True
                        camera.exposure = 0.004
                self.usb_camera_provider.needs_backup = True
            rosys.on_repeat(configure_cameras, 1.0)

            if self.field_friend.battery_control is not None:
                def check_if_charging():
                    if self.automator.is_running:
                        return
                    if self.field_friend.bms.state.is_charging:
                        self.was_charging = True
                        return
                    if not self.field_friend.bms.state.is_charging and self.was_charging:
                        self.automator.start(self.field_friend.battery_control.release_battery_relay())
                        self.was_charging = False

                def relase_relais_on_startup():
                    self.automator.start(self.field_friend.battery_control.release_battery_relay())

                self.was_charging = False
                rosys.on_repeat(check_if_charging, 0.5)
                rosys.on_startup(relase_relais_on_startup)
                # rosys.on_startup(self.start_esp)

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

    # def start_esp(self):
    #     self.log.info('>>>>>>>>>>starting esp')
    #     self.automator.start(self.enable_esp())

    # async def enable_esp(self):
    #     self.log.info('>>>>>>>>>>enabling esp because buggy')
    #     with open(f'/sys/class/gpio/export', 'w') as f:
    #         f.write('492\n')
    #     with open(f'/sys/class/gpio/export', 'w') as f:
    #         f.write('460\n')
    #     await rosys.sleep(0.1)
    #     self.field_friend.robot_brain.enable_esp()

    def _create_plant_locator(self, camera: rosys.vision.Camera) -> None:
        if camera == self.camera_selector.cameras['bottom_cam']:
            self.log.info(f'create plant locator for {camera.id}')
            self.plant_locator = PlantLocator(
                camera, self.detector, self.plant_provider, self.odometer
            )
            self.plant_locator.weed_category_names = self.big_weed_category_names + self.small_weed_category_names
            self.plant_locator.crop_category_names = ['sugar_beet', 'crop', 'coin_with_hole']
            self.plant_locator.minimum_crop_confidence = 0.3
            self.plant_locator.minimum_weed_confidence = 0.2

    def restart(self) -> None:
        os.utime('main.py')
