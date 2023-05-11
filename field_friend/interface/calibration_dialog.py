from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
from nicegui import ui
from nicegui.events import MouseEventArguments
from rosys.geometry import Point, Point3d
from rosys.vision import Calibration, Camera, CameraProvider, ImageSize


@dataclass
class CalibrationPoint:
    name: str
    world_position: Point3d
    image_position: Optional[Point] = None

    @staticmethod
    def create(name: str, x: float, y: float, z: float) -> 'CalibrationPoint':
        """Create a calibration point with the given name and world position."""
        return CalibrationPoint(name=name, world_position=Point3d(x=x, y=y, z=z))

    def svg_position(self, image_size: ImageSize) -> str:
        p = self.map_image_position(image_size)
        content = f'<line x1="{p.x}" y1="{p.y}" x2="{p.x - 14}" y2="{p.y}" stroke="red" stroke-width="1" />'
        content += f'<line x1="{p.x}" y1="{p.y}" x2="{p.x + 14}" y2="{p.y}" stroke="red" stroke-width="1" />'
        content += f'<line x1="{p.x}" y1="{p.y}" x2="{p.x}" y2="{p.y - 14}" stroke="red" stroke-width="1" />'
        content += f'<line x1="{p.x}" y1="{p.y}" x2="{p.x}" y2="{p.y + 14}" stroke="red" stroke-width="1" />'
        return content

    def svg_text(self, image_size: ImageSize) -> str:
        p = self.map_image_position(image_size)
        return f'<text x="{p.x - 15}" y="{p.y + 15}" stroke="red" fill="red" font-size="10">{self.name}</text>'

    def map_image_position(self, image_size: ImageSize) -> Point:
        return Point(x=min(max(self.image_position.x, 20), image_size.width - 20),
                     y=min(max(self.image_position.y, 20), image_size.height - 20))


class calibration_dialog(ui.dialog):

    def __init__(self, camera_provider: CameraProvider) -> None:
        super().__init__()
        self.log = logging.getLogger('field_friend.calibration')
        self.camera_provider = camera_provider
        self.points = [
            CalibrationPoint.create('A',  0.00,  0.10, 0.00),
            CalibrationPoint.create('B',  0.00,  0.00, 0.00),
            CalibrationPoint.create('B*', 0.00,  0.00, 0.05),
            CalibrationPoint.create('C',  0.00, -0.10, 0.00),

            CalibrationPoint.create('D',  0.10,  0.10, 0.00),
            CalibrationPoint.create('E',  0.10,  0.00, 0.00),
            CalibrationPoint.create('F',  0.10, -0.10, 0.00),

            CalibrationPoint.create('G',  0.20,  0.10, 0.00),
            CalibrationPoint.create('H',  0.20,  0.00, 0.00),
            CalibrationPoint.create('I',  0.20, -0.10, 0.00),
        ]
        self.active_point: Optional[CalibrationPoint] = None
        with self, ui.card().tight().style('max-width: 1000px'):
            self.calibration_image = ui.interactive_image(on_mouse=self.on_mouse_move,
                                                          events=['mousemove', 'mousedown', 'mouseup'],
                                                          cross=False).style('width: 900px')
            with ui.row().classes('m-4 justify-end items-baseline'):
                self.focal_length_input = ui.number('Focal length')
                ui.button('Apply', on_click=self.apply_calibration)

    async def edit(self, camera: Camera) -> bool:
        self.log.info(camera.id)
        self.image = camera.latest_captured_image
        if self.image is None:
            self.log.info('No image available')
            return False
        if camera.calibration:
            world_points = np.array([p.world_position.tuple for p in self.points])
            image_points = camera.calibration.project_array_to_image(world_points=world_points)
            for i, point in enumerate(self.points):
                point.image_position = Point(x=image_points[i][0], y=image_points[i][1])
        self.calibration_image.source = self.camera_provider.get_latest_image_url(camera)
        for point in self.points:
            if point.image_position is None:
                point.image_position = Point(x=self.image.size.width / 2, y=self.image.size.height / 2)
        self.draw_points()
        if camera.focal_length is None:
            camera.focal_length = 1830
        self.focal_length_input.value = camera.focal_length
        self.open()
        return (await self) or False

    def draw_points(self) -> None:
        svg = ''
        for point in self.points:
            svg += point.svg_position(self.image.size)
            if not any(p.image_position.distance(point.image_position) < 20 for p in self.points if p != point):
                svg += point.svg_text(self.image.size)
        self.calibration_image.content = svg

    def on_mouse_move(self, e: MouseEventArguments) -> None:
        if e.type == 'mouseup':
            self.active_point = None
            self.draw_points()
        if e.type == 'mousedown':
            self.active_point = self.closest_point(e.image_x, e.image_y)
        if e.type == 'mousemove' and self.active_point:
            self.active_point.image_position.x = e.image_x
            self.active_point.image_position.y = e.image_y
            self.draw_points()

    def closest_point(self, x: float, y: float) -> CalibrationPoint:
        return sorted(self.points, key=lambda p: p.map_image_position(self.image.size).distance(Point(x=x, y=y)))[0]

    def apply_calibration(self) -> None:
        camera = self.camera_provider.cameras[self.image.camera_id]
        try:
            camera.calibration = Calibration.from_points(world_points=[p.world_position for p in self.points],
                                                         image_points=[p.image_position for p in self.points],
                                                         image_size=self.image.size,
                                                         f0=self.focal_length_input.value)
        except Exception as e:
            camera.calibration = None
            ui.notify(str(e))
        else:
            ui.notify('Calibration applied')
            self.camera_provider.needs_backup = True
            self.submit(True)
