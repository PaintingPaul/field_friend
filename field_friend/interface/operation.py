
import logging
from typing import TYPE_CHECKING

import rosys
from nicegui import events, ui

from .automation_controls import automation_controls
from .field_friend_object import field_friend_object
from .field_object import field_object
from .key_controls import KeyControls
from .plant_object import plant_objects
from .visualizer_object import visualizer_object

if TYPE_CHECKING:
    from field_friend.system import System

SHORTCUT_INFO = '''
    Steer the robot manually with the JOYSTICK.<br>
    Or hold SHIFT and use the ARROW KEYS
'''


class operation:

    def __init__(self, system: 'System') -> None:
        self.log = logging.getLogger('field_friend.operation')
        self.system = system
        self.field_provider = system.field_provider
        self.field = None

        with ui.card().tight():
            with ui.column().classes('m-2'):
                with ui.row():
                    key_controls = KeyControls(self.system)
                    rosys.driving.joystick(self.system.steerer, size=50, color='#6E93D6').classes(
                        'm-2').style('width:10em; height:10em;')
                    with ui.column().classes('mt-4'):
                        ui.markdown(SHORTCUT_INFO).classes('col-grow')
                        ui.number('speed', format='%.0f', max=4, min=1, value=1).props('dense outlined').classes(
                            'w-24 mr-4').bind_value(key_controls, 'speed').tooltip('Set the speed of the robot (1-4)')

                        with ui.dialog() as dialog, ui.card():
                            ui.label('Do you want to continue the old mowing automation?')
                            with ui.row():
                                ui.button('Yes', on_click=lambda: dialog.submit('Yes'))
                                ui.button('No', on_click=lambda: dialog.submit('No'))
                                ui.button('Cancel', on_click=lambda: dialog.submit('Cancel'))

                with ui.row():
                    automations_toggle = ui.toggle(
                        [key for key in self.system.automations.keys()],
                        value='weeding').bind_value(
                        self.system.automator, 'default_automation', forward=lambda key: self.system.automations[key],
                        backward=lambda automation: next(
                            key for key, value in self.system.automations.items() if value == automation))
                with ui.column().bind_visibility_from(automations_toggle, 'value', value='mowing'):
                    with ui.row():
                        ui.number('padding', value=0.5, step=0.1, min=0.0, format='%.1f').props('dense outlined suffix=m').classes(
                            'w-24').bind_value(system.mowing, 'padding').tooltip('Set the padding for the mowing automation')
                        ui.number('lane distance', value=0.5, step=0.1, min=0.0, format='%.1f').props('dense outlined suffix=m').classes(
                            'w-24').bind_value(system.mowing, 'lane_distance').tooltip('Set the lane distance for the system. automation')
                        ui.number('number of outer lanes', value=3, step=1, min=3, format='%.0f').props('dense outlined').classes(
                            'w-24').bind_value(system.mowing, 'number_of_outer_lanes').tooltip('Set the number of outer lanes for the mowing automation')

                with ui.column().bind_visibility_from(automations_toggle, 'value', value='demo_weeding'):
                    if system.field_friend.z_axis:
                        ui.number('Drill depth', format='%.2f', value=0.05, step=0.01, min=0.01, max=0.18).props('dense outlined suffix=m').classes(
                            'w-24').bind_value(system.demo_weeding, 'drill_depth').tooltip('Set the drill depth for the weeding automation')
                        ui.label('press PLAY to start weeding with the set drill depth')
                    else:
                        ui.label('This Field Friend has no weeding tool available')

                with ui.column().bind_visibility_from(automations_toggle, 'value', value='weeding'):
                    with ui.row():
                        mode = ui.toggle(
                            ['Bohren', 'Hacken'],
                            value='Bohren').bind_value(
                            system.demo_weeding, 'mode').props('outline')
                        ui.number(
                            'Drill depth', format='%.2f', value=0.05, step=0.01, min=0.01, max=0.18).props(
                            'dense outlined suffix=m').classes('w-24').bind_value(
                            self.system.weeding, 'drill_depth').tooltip(
                            'Set the drill depth for the weeding automation').bind_visibility_from(
                            mode, 'value', value='Bohren')

                with ui.column().bind_visibility_from(automations_toggle, 'value', value='Continuous weeding'):
                    with ui.row():
                        ui.number(
                            'Drill depth', format='%.2f', value=0.05, step=0.01, min=0.01, max=0.18).props(
                            'dense outlined suffix=m').classes('w-24').bind_value(
                            self.system.weeding_new, 'drill_depth').tooltip(
                            'Set the drill depth for the weeding automation')

                with ui.column().bind_visibility_from(automations_toggle, 'value', value='collecting'):
                    with ui.row():
                        ui.number(
                            'Drill angle', format='%.0f', value=100, step=1, min=1, max=180).props(
                            'dense outlined suffix=m').classes('w-24').bind_value(
                            self.system.coin_collecting, 'angle').tooltip(
                            'Set the drill depth for the weeding automation')
                        ui.checkbox('with drilling', value=True).bind_value(
                            self.system.coin_collecting, 'with_drilling')

                with ui.column().bind_visibility_from(automations_toggle, 'value', value='control_panel'):
                    with ui.row():
                        with ui.card().tight():
                            mode = ui.toggle(
                                ['Forward', 'Backward', 'Both', 'Circle'],
                                value='Forward').bind_value(
                                system.control_panel, 'mode').props('outline').tooltip('Select the driving mode.')
                    with ui.row():
                        with ui.card().tight():
                            with ui.expansion('Set Target', value=True, icon='ads_click'):
                                def distance_visibility(mode):
                                    return mode in ['Forward', 'Backward', 'Both']
                                ui.checkbox('Loop', value=True).tooltip(
                                    'Execute Automation in an infinite loop').bind_value(self.system.control_panel, 'loop').bind_visibility_from(mode, 'value', value='Both')
                                # ui.checkbox('Loop', value=True).tooltip(
                                # 'Drive forward and backward in an infinite loop').bind_value(self.system.control_panel, 'loop').bind_visibility_from(mode, 'value', value='Circle')
                                select_target_swith = ui.checkbox('Click to select Coordinates', value=False).tooltip(
                                    'Click in the 3D view to select a target point')
                                with ui.row():
                                    ui.number(
                                        'x-Coordinate', format='%.2f', value=0.00, step=0.1).props(
                                        'dense outlined suffix=m').classes('w-24').bind_value(
                                        self.system.control_panel, 'target_point_x').tooltip(
                                        'Set the x-coordinate for the target point')
                                    ui.number(
                                        'y-Coordinate', format='%.2f', value=0.00, step=0.1).props(
                                        'dense outlined suffix=m').classes('w-24').bind_value(
                                        self.system.control_panel, 'target_point_y').tooltip(
                                        'Set the y-coordinate for the target point')
                                with ui.row().bind_visibility_from(mode, 'value', backward=distance_visibility):
                                    ui.number(
                                        'Distance', format='%.2f', value=0.00, step=0.1).props(
                                        'dense outlined suffix=m').classes('w-24').bind_value(
                                        self.system.control_panel, 'target_distance').tooltip(
                                        'Set the distance for the target point')
                                    ui.button('Set', on_click=self.system.control_panel.calc_target_by_distance).tooltip(
                                        'Set the target point depending on the given distance.')
                                with ui.row().bind_visibility_from(mode, 'value', value='Circle'):
                                    ui.number(
                                        'Radius', format='%.2f', value=0.00, step=0.5).props(
                                        'dense outlined suffix=m').classes('w-24').bind_value(
                                        self.system.control_panel, 'radius').tooltip(
                                        'Set the circle radius')
                        with ui.card().tight():
                            with ui.expansion('Change Yaw', value=True, icon='flip_camera_android'):
                                with ui.row():
                                    yaw_knob = ui.knob(0.0, show_value=True, track_color='grey-2',
                                                       min=0, max=360).props('reverse = True').bind_value(self.system.control_panel, 'set_yaw')
                                    ui.button('Set Yaw', on_click=self.system.control_panel.robot_rotate)
                                ui.number(
                                    'Yaw', format='%.2f', value=0.00, min=0, max=360).props(
                                    'dense outlined suffix=m').classes('w-32').bind_value(yaw_knob).tooltip(
                                    'Rotate the robot')

                with ui.row().classes('items-center'):
                    async def ensure_start() -> bool:
                        self.log.info('Ensuring start of automation')
                        if not automations_toggle.value == 'mowing' or self.system.mowing.current_path is None:
                            return True
                        result = await dialog
                        if result == 'Yes':
                            self.system.mowing.continue_mowing = True
                        elif result == 'No':
                            self.system.mowing.continue_mowing = False
                        elif result == 'Cancel':
                            return False
                        return True
                    automation_controls(self.system.automator, can_start=ensure_start)

                    @ui.refreshable
                    def show_field_selection() -> None:
                        def set_field() -> None:
                            for field in self.system.field_provider.fields:
                                if field.id == self.field_selection.value:
                                    self.field = field
                                    self.system.weeding.field = field
                                    self.system.weeding_new.field = field
                                    show_row_selection.refresh()

                        field_selection_dict = {}
                        for field in self.system.field_provider.fields:
                            field_selection_dict[field.id] = field.name

                        self.field_selection = ui.select(
                            field_selection_dict,
                            with_input=True, on_change=set_field, label='Field').tooltip(
                            'Select the field to weed').classes('w-24')
                        show_row_selection()

                    @ui.refreshable
                    def show_row_selection() -> None:
                        def set_row() -> None:
                            for row in self.field.rows:
                                if row.id == self.row_selection.value:
                                    self.system.weeding.row = row
                                    self.system.weeding_new.start_row = row
                        if self.field is not None:
                            row_selection_dict = {}
                            if self.field is not None:
                                for row in self.field.rows:
                                    row_selection_dict[row.id] = row.name

                            self.row_selection = ui.select(
                                row_selection_dict,
                                label='Row', with_input=True, on_change=set_row).tooltip(
                                'Select the row to weed').classes('w-24')
                    show_field_selection()
                    self.system.field_provider.FIELDS_CHANGED.register(show_field_selection.refresh)

                # with ui.row().classes('m-4'):
                    ui.button('emergency stop', on_click=lambda: system.field_friend.estop.set_soft_estop(True)).props('color=red').classes(
                        'py-3 px-6 text-lg').bind_visibility_from(system.field_friend.estop, 'is_soft_estop_active', value=False)
                    ui.button('emergency reset', on_click=lambda: system.field_friend.estop.set_soft_estop(False)).props(
                        'color=red-700 outline').classes('py-3 px-6 text-lg').bind_visibility_from(system.field_friend.estop,
                                                                                                   'is_soft_estop_active', value=True)
                    # ui.checkbox(
                    #     'Space bar emergency stop').tooltip(
                    #     'Enable or disable the emergency stop on space bar').bind_value(key_controls, 'estop_on_space')
