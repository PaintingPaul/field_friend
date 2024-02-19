import logging
import math
from typing import TYPE_CHECKING, Callable, Literal, Optional

import rosys
# from nicegui.events import SceneClickEventArguments
from rosys.driving import Driver
from rosys.driving.odometer import Odometer
from rosys.geometry import Point

from ..hardware import FieldFriend


class ControlPanel:
    def __init__(self, field_friend: FieldFriend, driver: Driver, odometer: Odometer) -> None:
        self.log = logging.getLogger('field_friend.control_panel')
        self.field_friend = field_friend
        self.driver = driver
        self.odometer = odometer
        self.mode: Literal['Forward', 'Backward', 'Both'] = 'Forward'
        self.target_point_x: float = 0.00
        self.target_point_y: float = 0.00
        self.target_distance: float = 0.00
        self.set_yaw: float = 0.00
        self.loop: bool = True
        self.select_coordinates: bool = False
        self.radius: float = 0.00

    # async def handle_click(self, event: SceneClickEventArguments):
    #     for hit in event.hits:
    #         if hit.object_id == 'ground':
    #             self.target_point_x = hit.x
    #             self.target_point_y = hit.y

    async def start(self) -> None:
        if self.mode == 'Forward':
            await self.drive_forward()
        if self.mode == 'Backward':
            await self.drive_backward()
        if self.mode == 'Both':
            await self.drive_forward_backward()
        if self.mode == 'Circle':
            await self.drive_circle()

    # Here is a bug that needs to be fixed!
    def calc_target_by_distance(self):
        current_x = self.odometer.prediction.x
        current_y = self.odometer.prediction.y
        self.target_point_x = (current_x + self.target_distance * math.cos(self.odometer.prediction.yaw))
        self.target_point_y = (current_y + self.target_distance * math.sin(self.odometer.prediction.yaw))

    async def drive_forward_backward(self) -> None:
        start = self.odometer.prediction
        while self.loop:
            await self.drive_forward()
            # rosys.notify(f'Startpoint: {start}')
            await self.drive_backward(target_behind=start)

    # async def drive_to_target(self, target, current_position) -> None:
    #     if Point.distance(current_position, target) > 0.02:
    #         await self.driver.drive_to(target)
    #     else:
    #         await rosys.notify('Target to close', 'negative')

    async def drive_forward(self, target_in_front=None) -> None:
        """Function checks the current Position of the robot based on the prediction of the robots odometer. A target is calculated in front of the robot based on the robot's current position and the robot drives forward to the target"""
        predicted_pose = self.odometer.prediction
        target = rosys.geometry.Point(x=self.target_point_x, y=self.target_point_y)
        # await self.driver.drive_to(target) if Point.distance(predicted_pose, target) > 0.02 else rosys.notify('Target to close', 'negative') #uncommon way of using a tenary operator
        if target_in_front is None:
            if Point.distance(target, predicted_pose) > 0.02:
                await self.driver.drive_to(target)
            else:
                await rosys.notify('Target to close', 'negative')
        else:
            await self.driver.drive_to(target_in_front)

        # rosys.notify(f'Drive Forward completed! Current Position: {self.odometer.prediction.point}', 'positive')

    async def drive_backward(self, target_behind=None) -> None:
        """Function checks the current Position of the robot based on the prediction of the robots odometer. A target is calculated behind the robot based on the robot's current position and the robot drives backward to the target"""
        predicted_pose = self.odometer.prediction
        target = rosys.geometry.Point(x=self.target_point_x, y=self.target_point_y)
        if target_behind is None:
            if Point.distance(target, predicted_pose) > 0.02:
                await self.driver.drive_to(target, backward=True)
            else:
                await rosys.notify('Target to close', 'negative')
        else:
            await self.driver.drive_to(target_behind, backward=True)

        # rosys.notify(f'Drive Backward completed! Current Position: {self.odometer.prediction.point}', 'positive')

    async def robot_rotate(self):
        self.driver.parameters.angular_speed_limit = 0.1
        self.driver.parameters.linear_speed_limit = 0.1
        self.driver.parameters.minimum_turning_radius = 0.001
        await self.driver.rotate(self.set_yaw)
        await self.field_friend.wheels.stop()

    async def drive_circle(self):
        await self.driver.drive_circle_radius(self.radius)
        await self.field_friend.wheels.stop()
