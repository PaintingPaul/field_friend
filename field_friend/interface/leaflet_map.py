
import logging
import uuid
from copy import deepcopy
from typing import TYPE_CHECKING, Dict, List, Union

import numpy as np
import rosys
import rosys.geometry
from geographiclib.geodesic import Geodesic
from nicegui import elements, events, ui

from field_friend.navigation.point_transformation import cartesian_to_wgs84, wgs84_to_cartesian

from ..automations import Field, FieldProvider
from .key_controls import KeyControls

if TYPE_CHECKING:
    from field_friend.system import System


class leaflet_map:
    def __init__(self, system: 'System', draw_tools: bool) -> None:
        self.log = logging.getLogger('field_friend.leaflet_map')
        self.system = system
        self.field_provider = system.field_provider
        self.key_controls = KeyControls(self.system)
        self.draw_tools = draw_tools
        self.gnss = system.gnss
        self.draw_control = {
            'draw': {
                'polygon': True,
                'marker': True,
                'circle': False,
                'rectangle': False,
                'polyline': False,
                'circlemarker': False,
            },
            'edit': False,
        }
        self.center_point = [51.983159, 7.434212]
        if self.field_provider.active_field is None:
            self.center_point = [51.983159, 7.434212]
        else:
            if len(self.field_provider.active_field.outline_wgs84) > 0:
                self.center_point = self.field_provider.active_field.outline_wgs84[0]
        if draw_tools:
            self.m = ui.leaflet(center=(self.center_point[0], self.center_point[1]),
                                zoom=13, draw_control=self.draw_control)
        else:
            self.m = ui.leaflet(center=(self.center_point[0], self.center_point[1]),
                                zoom=13)
        self.field_layers: list[list] = []
        self.robot_marker = None
        self.drawn_marker = None
        self.is_real: bool = False
        self.target_marker_list: list = []
        self.obstacle_layers: list = []
        self.row_layers: list = []
        self.update_layers()
        self.visualize_active_field()
        self.field_provider.FIELDS_CHANGED.register(self.update_layers)
        self.field_provider.FIELD_SELECTED.register(self.visualize_active_field)
        self.field_provider.FIELDS_CHANGED.register(self.visualize_active_field)

        def handle_draw(e: events.GenericEventArguments):
            if e.args['layerType'] == 'marker':
                latlon = (e.args['layer']['_latlng']['lat'],
                          e.args['layer']['_latlng']['lng'])
                self.drawn_marker = self.m.marker(latlng=latlon)
                if system.is_real:
                    with ui.dialog() as real_marker_dialog, ui.card():
                        ui.label('You are currently working in a real system. What does the placed point represent?')
                        ui.button('add point to selected object (row, obstacle)',
                                  on_click=lambda: self.add_point_active_object(latlon, real_marker_dialog))
                        ui.button('Close', on_click=lambda: self.abort_point_drawing(real_marker_dialog))
                    real_marker_dialog.open()
                else:
                    with ui.dialog() as simulated_marker_dialog, ui.card():
                        ui.label('You are currently working in a simulation. What does the placed point represent?')
                        ui.button('simulated roboter reference point',
                                  on_click=lambda: self.set_simulated_reference(latlon, simulated_marker_dialog))
                        ui.button('as point for the current object',
                                  on_click=lambda: self.add_point_active_object(latlon, simulated_marker_dialog))
                        ui.button('Close', on_click=lambda: self.abort_point_drawing(simulated_marker_dialog))
                    simulated_marker_dialog.open()
            if e.args['layerType'] == 'polygon':
                coordinates = e.args['layer']['_latlngs']
                point_list = []
                for point in coordinates[0]:
                    point_list.append([point['lat'], point['lng']])
                field = Field(id=f'{str(uuid.uuid4())}', name=f'{str(uuid.uuid4())}',
                              outline_wgs84=point_list, reference_lat=point_list[0][0], reference_lon=point_list[0][1])
                self.field_provider.add_field(field)

        def handle_place_target(e: events.GenericEventArguments):
            if self.system.automator.default_automation == self.system.automations['control_panel'] and self.system.control_panel.select_coordinates:
                lat = e.args['latlng']['lat']
                lng = e.args['latlng']['lng']
                self.target_marker_list.append(self.m.marker(latlng=(lat, lng)))
                with ui.dialog() as target_marker_dialog, ui.card():
                    if self.is_real:
                        ui.label('Sorry, this feature currently only works in the simulation.')
                        ui.button('Close', on_click=lambda: self.abort_point_drawing(target_marker_dialog))
                    else:
                        ui.label('You are currently working in a simulation. Set the target the robot should drive to.')
                        ui.button('Set target point', on_click=lambda: self.set_target_point(
                            lat, lng, target_marker_dialog))
                        ui.button('Abort', on_click=lambda: self.abort_point_drawing(target_marker_dialog))
                    target_marker_dialog.open()

        ui.checkbox('Is Real').bind_value(self, 'is_real')

        with self.m as m:
            m.on('map-click', handle_place_target)

        with self.m as m:
            m.on('draw:created', handle_draw)
        self.gnss.ROBOT_POSITION_LOCATED.register(self.update_robot_position)

    def set_simulated_reference(self, latlon, dialog):
        dialog.close()
        self.m.remove_layer(self.drawn_marker)
        self.gnss.set_reference(latlon[0], latlon[1])
        self.gnss.ROBOT_POSITION_LOCATED.emit()
        self.gnss.ROBOT_POSE_LOCATED.emit(rosys.geometry.Pose(
            x=0.000,
            y=0.000,
            yaw=0.0,
            time=0
        ))
        ui.notify(f'Robot reference has been set to {latlon[0]}, {latlon[1]}')

    def set_target_point(self, lat, lng, dialog):
        dialog.close()
        if len(self.target_marker_list) > 1:
            self.m.remove_layer(self.target_marker_list.pop(-2))
        reference_point = [self.gnss.reference_lat, self.gnss.reference_lon]
        rosys.notify(f'Reference: {reference_point}')
        target_point = [lat, lng]
        rosys.notify(f'Target: {target_point}')
        cartesian_coords = wgs84_to_cartesian(reference_point, target_point)
        self.system.control_panel.target_point_y = cartesian_coords[0]
        self.system.control_panel.target_point_x = cartesian_coords[1]*-1

    def abort_point_drawing(self, dialog) -> None:
        if self.drawn_marker is not None:
            self.m.remove_layer(self.drawn_marker)
        self.drawn_marker = None
        if len(self.target_marker_list) > 0:
            self.m.remove_layer(self.target_marker_list.pop())
        dialog.close()

    def add_point_active_object(self, latlon, dialog) -> None:
        dialog.close()
        self.m.remove_layer(self.drawn_marker)
        if self.field_provider.active_object is not None and self.field_provider.active_object["object"] is not None:
            self.field_provider.active_object["object"].points_wgs84.append([latlon[0], latlon[1]])
            self.field_provider.OBJECT_SELECTED.emit()
            self.visualize_active_field()
        else:
            ui.notify("No object selected. Point could not be added to the void.")

    def visualize_active_field(self) -> None:
        if self.field_provider.active_field is not None:
            for field in self.field_layers:
                field.run_method(':setStyle', "{'color': '#6E93D6'}")
            for layer in self.obstacle_layers:
                self.m.remove_layer(layer)
            self.obstacle_layers = []
            for layer in self.row_layers:
                self.m.remove_layer(layer)
            self.row_layers = []
            if self.field_provider.active_field is not None:
                layer_index = self.field_provider.fields.index(self.field_provider.active_field)
                self.m.remove_layer(self.field_layers[layer_index])
                self.field_layers[layer_index] = self.m.generic_layer(
                    name="polygon", args=[self.field_provider.active_field.outline_wgs84, {'color': '#999'}])
                for obstacle in self.field_provider.active_field.obstacles:
                    self.obstacle_layers.append(self.m.generic_layer(
                        name="polygon", args=[obstacle.points_wgs84, {'color': '#C10015'}]))
                for row in self.field_provider.active_field.rows:
                    self.row_layers.append(self.m.generic_layer(
                        name="polyline", args=[row.points_wgs84, {'color': '#F2C037'}]))

    def update_layers(self) -> None:
        for layer in self.field_layers:
            self.m.remove_layer(layer)
        self.field_layers = []
        for field in self.field_provider.fields:
            self.field_layers.append(self.m.generic_layer(name="polygon", args=[
                                     field.outline_wgs84, {'color': '#6E93D6'}]))

    def update_robot_position(self) -> None:
        if self.robot_marker is None:
            self.robot_marker = self.m.marker(latlng=(self.gnss.record.latitude, self.gnss.record.longitude))
        icon = 'L.icon({iconUrl: "assets/robot_position.svg", iconSize: [40,40], iconAnchor:[20,20]})'
        self.robot_marker.run_method(':setIcon', icon)
        self.robot_marker.move(self.gnss.record.latitude, self.gnss.record.longitude)

    def change_basemap(self) -> None:
        return
        # TODO: add a button in leaflet map to change basemap layer and implement the functionality here

        # this is the ESRI satellite  image as free satellite image
        # Esri_WorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        #     attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        # })
