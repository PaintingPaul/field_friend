#!/usr/bin/env python3
from nicegui import app, ui
from rosys.hardware import imu 
import field_friend.log_configuration as log_configuration
from field_friend import interface
from field_friend.system import System

logger = log_configuration.configure()
app.add_static_files('/assets', 'assets')


def startup() -> None:
    system = System()
    #i = imu()
    @ui.page('/')
    def page(dev: bool = False) -> None:
        ui.colors(primary='#6E93D6', secondary='#53B689', accent='#111B1E', positive='#53B689')
        status_drawer = interface.status_drawer(system.field_friend, system.gnss, system.odometer)
        interface.header_bar(system, status_drawer)
        with ui.column().classes('w-full items-stretch'):
            with ui.row().classes('items-stretch justify-items-stretch').style('flex-wrap:nowrap'):
                interface.operation(system)
                interface.cameras(system.camera_selector, system.usb_camera_provider, system.automator,
                                  system.detector, system.puncher, version=system.field_friend.version)
            if dev:
                with ui.row().classes('items-stretch justify-items-stretch'):
                    interface.development(system.field_friend)
                    interface.hardware_control(system.field_friend, system.automator, system.puncher)

    @ui.page('/dev')
    def dev_page():
        page(dev=True)

    @ui.page('/calibrate')
    def calibrate_page(dev: bool = True):
        ui.colors(primary='#6E93D6', secondary='#53B689', accent='#111B1E', positive='#53B689')
        status_drawer = interface.status_drawer(system.field_friend, system.gnss, system.odometer)
        interface.header_bar(system, status_drawer)
        interface.system_bar()
        with ui.column().classes('w-full items-stretch'):
            with ui.row().classes('items-stretch justify-items-stretch').style('flex-wrap:nowrap'):
                interface.operation(system)
                interface.calibrate(system.rolling, system.field_friend.imu)
            if dev:
                with ui.row().classes('items-stretch justify-items-stretch'):
                    interface.development(system.field_friend)
                    interface.hardware_control(system.field_friend, system.automator, system.puncher)

    @ui.page('/field')
    def field_page(dev: bool = True):
        ui.colors(primary='#6E93D6', secondary='#53B689', accent='#111B1E', positive='#53B689')
        status_drawer = interface.status_drawer(system.field_friend, system.gnss, system.odometer)
        interface.header_bar(system, status_drawer)
        interface.system_bar()
        with ui.column().classes('w-full items-stretch'):
            with ui.row().classes('items-stretch justify-items-stretch').style('flex-wrap:nowrap'):
                interface.operation(system)
                interface.field_planner(system.field_provider, system.odometer, system.gnss)
            if dev:
                with ui.row().classes('items-stretch justify-items-stretch'):
                    interface.development(system.field_friend)
                    interface.hardware_control(system.field_friend, system.automator, system.puncher)

    @ui.page('/path')
    def path_page(dev: bool = True):
        ui.colors(primary='#6E93D6', secondary='#53B689', accent='#111B1E', positive='#53B689')
        status_drawer = interface.status_drawer(system.field_friend, system.gnss, system.odometer)
        interface.header_bar(system, status_drawer)
        interface.system_bar()
        with ui.column().classes('w-full items-stretch'):
            with ui.row().classes('items-stretch justify-items-stretch').style('flex-wrap:nowrap'):
                interface.operation(system)
                interface.path_planner(system.path_provider, system.path_recorder, system.automator)
            if dev:
                with ui.row().classes('items-stretch justify-items-stretch'):
                    interface.development(system.field_friend)
                    interface.hardware_control(system.field_friend, system.automator, system.puncher)

    @ui.page('/test')
    def test_page():
        status_drawer = interface.status_drawer(system.field_friend, system.gnss, system.odometer)
        interface.header_bar(system, status_drawer)
        interface.system_bar()
        with ui.column().classes('w-full items-stretch'):
            with ui.row().classes('items-stretch justify-items-stretch').style('flex-wrap:nowrap'):
                interface.test(system.field_friend, system.steerer, system.odometer, system.automator, system.driver,
                               system.usb_camera_provider)

    @app.get('/status')
    def status():
        return {'status': 'ok'}


app.on_startup(startup)

ui.run(title='Field Friend', port=8080, favicon='assets/favicon.ico')
