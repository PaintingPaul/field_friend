import colorsys
import logging
from typing import Optional

import numpy as np
from nicegui import app, ui
from nicegui.elements.card import Card
from nicegui.events import MouseEventArguments, ValueChangeEventArguments
from rosys import background_tasks
from rosys.automation import Automator
from rosys.geometry import Point, Point3d
from rosys.vision import Camera, CameraProvider, Detector

from ..automations import Puncher
from ..vision import CameraSelector
from .calibration_dialog import calibration_dialog


class CameraCard(Card):

    def __init__(
            self, camera_type: str, camera_provider: CameraProvider, camera_selector: CameraSelector,
            automator: Automator, detector: Detector, puncher: Optional[Puncher] = None, *, version: str,
            shrink_factor: int = 1) -> None:
        super().__init__()
        self.log = logging.getLogger('field_friend.camera_card')
        self.camera_type = camera_type
        self.camera = None
        self.camera_provider = camera_provider
        self.camera_selector = camera_selector
        self.automator = automator
        self.detector = detector
        self.capture_images = ui.timer(1, lambda: background_tasks.create(
            self.detector.upload(self.camera.latest_captured_image)), active=False)
        self.puncher = puncher
        self.shrink_factor = shrink_factor
        self.image_view: ui.interactive_image = None
        self.calibration_dialog = calibration_dialog(camera_provider, version=version)
        with self.tight().classes('col gap-4').style('width:640px'):
            ui.image('assets/field_friend.webp').classes('w-full')
            ui.label(f'no {camera_type} available').classes('text-center')
        ui.timer(1, self.update_content)

    def update_content(self) -> None:
        if self.camera is None:
            self.log.info(f'looking for {self.camera_type}')
            for camera_type, camera in self.camera_selector.cameras.items():
                self.log.info(f'found {camera_type} {camera.id}')
                self.use_camera((camera_type, camera))

    def use_camera(self, camera_data: tuple[str, Camera]) -> None:
        camera_type, camera = camera_data
        if camera_type != self.camera_type:
            self.log.info(f'ignoring camera (expected {self.camera_type})')
            return
        self.camera = camera
        self.clear()
        events = ['mousemove', 'mouseout', 'mouseup']
        with self:
            with ui.row().classes('w-full items-center').style('gap:0.5em;margin-left:1em;margin-right:1em'):
                ui.label(f'{camera_type}:').classes('text-xl')
            self.image_view = ui.interactive_image(
                '',
                cross=True,
                on_mouse=self.on_mouse_move,
                events=events
            ).classes('w-full')

            def update():
                if self.shrink_factor > 1:
                    url = f'{self.camera_provider.get_latest_image_url(camera)}?shrink={self.shrink_factor}'
                else:
                    url = self.camera_provider.get_latest_image_url(camera)
                self.image_view.set_source(url)

            ui.timer(1, update)
            with ui.row().classes('m-4 justify-end items-center'):
                self.depth = ui.number('punch depth', value=0.02, format='%.2f', step=0.01, min=0.01, max=0.18)
                ui.checkbox('Capture Images').bind_value_to(self.capture_images, 'active') \
                    .tooltip('Record new images for the Learning Loop')
                self.show_mapping_checkbox = ui.checkbox('Show Mapping', on_change=self.show_mapping) \
                    .tooltip('Show the mapping between camera and world coordinates')
                ui.button('calibrate', on_click=self.calibrate) \
                    .props('icon=straighten outline').tooltip('Calibrate camera')
            with ui.row():
                self.debug_position = ui.label()

    def on_mouse_move(self, e: MouseEventArguments):
        if e.type == 'mousemove':
            point2d = Point(x=e.image_x, y=e.image_y)
            point3d = self.camera.calibration.project_from_image(point2d)
            self.debug_position.set_text(f'{point2d} -> {point3d}')
        if e.type == 'mouseup':
            point2d = Point(x=e.image_x, y=e.image_y)
            point3d = self.camera.calibration.project_from_image(point2d)
            if point3d is not None:
                self.debug_position.set_text(f'last punch: {point2d} -> {point3d}')
                if self.puncher is not None and self.shrink_factor == 1:
                    self.log.info(f'punching {point3d}')
                    self.automator.start(self.puncher.drive_and_punch(point3d.x, point3d.y, self.depth.value))
        if e.type == 'mouseout':
            self.debug_position.set_text('')

    async def calibrate(self) -> None:
        result = await self.calibration_dialog.edit(self.camera)
        if result:
            self.show_mapping_checkbox.value = True

    def show_mapping(self, event: ValueChangeEventArguments) -> None:
        if not event.value:
            self.image_view.content = ''
            return

        world_points = np.array([[x, y, 0] for x in np.linspace(0, 0.3, 15) for y in np.linspace(-0.2, 0.2, 20)])
        image_points = self.camera.calibration.project_array_to_image(world_points)
        colors_rgb = [colorsys.hsv_to_rgb(f, 1, 1) for f in np.linspace(0, 1, len(world_points))]
        colors_hex = [f'#{int(rgb[0] * 255):02x}{int(rgb[1] * 255):02x}{int(rgb[2] * 255):02x}' for rgb in colors_rgb]
        self.image_view.content = ''.join(f'<circle cx="{p[0]}" cy="{p[1]}" r="2" fill="{color}"/>'
                                          for p, color in zip(image_points, colors_hex))


class cameras:

    def __init__(
            self, camera_selector: CameraSelector, camera_provider: CameraProvider,
            automator: Automator, detector: Detector,
            puncher: Optional[Puncher] = None, *, version: str, shrink_factor: int = 1) -> None:
        self.log = logging.getLogger('field_friend.cameras')
        self.camera_selector = camera_selector
        self.camera_provider = camera_provider
        self.automator = automator
        self.detector = detector
        self.puncher = puncher
        self.shrink_factor = shrink_factor
        self.version = version
        self.cards: dict[str, CameraCard] = {}
        self.camera_grid = ui.row()
        ui.timer(1, self.update_cameras)

    def update_cameras(self) -> None:
        with self.camera_grid:
            if set(self.camera_selector.camera_ids.keys()) != set(self.cards.keys()):
                self.camera_grid.clear()
                for camera_type in self.camera_selector.camera_ids.keys():
                    self.cards[camera_type] = CameraCard(
                        camera_type, self.camera_provider, self.camera_selector, self.automator, self.detector, self.
                        puncher, version=self.version, shrink_factor=self.shrink_factor)
