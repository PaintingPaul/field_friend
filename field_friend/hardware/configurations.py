fieldfriend_configurations = {
    'u1': {
        'params': {
            'motor_gear_ratio': 12.52,
            'thooth_count': 17,
            'pitch': 0.041,
            'wheel_distance': 0.47,
            'work_x': 0.07,
            'drill_radius': 0.025,
        },
        'robot_brain': {
            'flash_params': ['nand'],
        },
        'bluetooth': {
            'name': 'uckerbot-u1',
        },
        'serial': {
            'name': 'serial',
            'rx_pin': 26,
            'tx_pin': 27,
            'baud': 115200,
            'num': 1,
        },
        'expander': {
            'name': 'p0',
            'boot': 25,
            'enable': 14,
        },
        'can': {
            'name': 'can',
            'on_expander': False,
            'rx_pin': 32,
            'tx_pin': 33,
            'baud': 1_000_000,
        },
        'wheels': {
            'version': 'double_wheels',
            'name': 'wheels',
            'left_back_can_address': 0x000,
            'left_front_can_address': 0x100,
            'right_back_can_address': 0x200,
            'right_front_can_address': 0x300,
            'is_left_reversed': False,
            'is_right_reversed': True,
        },
        'y_axis': {
            'version': 'none',
        },
        'z_axis': {
            'version': 'none',
        },
        'flashlight': {
            'version': 'flashlight',
            'name': 'flashlight',
            'pin': 5,
            'on_expander': True,
        },
        'estop': {
            'name': 'estop',
            'pins': {'1': 34, '2': 35},
        },
        'bms': {
            'name': 'bms',
            'on_expander': True,
            'rx_pin': 26,
            'tx_pin': 27,
            'baud': 9600,
            'num': 1,
        },
        'imu': {
            'name': 'imu',
        },
    },
    'u2': {
        'params': {
            'motor_gear_ratio': 12.52,
            'thooth_count': 17,
            'pitch': 0.041,
            'wheel_distance': 0.47,
            'work_x_chop': 0.035,
            'work_x_drill': 0.1675,
            'drill_radius': 0.025,
            'chop_radius': 0.07,
        },
        'robot_brain': {
            'flash_params': ['nand']
        },
        'bluetooth': {
            'name': 'uckerbot-u2',
        },
        'serial': {
            'name': 'serial',
            'rx_pin': 26,
            'tx_pin': 27,
            'baud': 115200,
            'num': 1,
        },
        'expander': {
            'name': 'p0',
            'boot': 25,
            'enable': 14,
        },
        'can': {
            'name': 'can',
            'on_expander': False,
            'rx_pin': 32,
            'tx_pin': 33,
            'baud': 1_000_000,
        },
        'wheels': {
            'version': 'double_wheels',
            'name': 'wheels',
            'left_back_can_address': 0x000,
            'left_front_can_address': 0x100,
            'right_back_can_address': 0x200,
            'right_front_can_address': 0x300,
            'is_left_reversed': False,
            'is_right_reversed': True,
        },
        'y_axis': {
            'version': 'chain_axis',
            'name': 'chain_axis',
            'motor_on_expander': False,
            'end_stops_on_expander': True,
            'step_pin': 5,
            'dir_pin': 4,
            'alarm_pin': 13,
            'ref_t_pin': 21,
        },
        'z_axis': {
            'version': 'z_axis_v2',
            'name': 'z_axis',
            'step_pin': 5,
            'dir_pin': 4,
            'alarm_pin': 33,
            'ref_t_pin': 25,
            'end_b_pin': 22,
            'motor_on_expander': True,
            'end_stops_on_expander': True,
            'ref_t_inverted': False,
            'end_b_inverted':  False,
            'ccw': False,
        },
        'flashlight': {
            'version': 'flashlight_v2',
            'name': 'flashlight',
            'front_pin': 12,
            'back_pin': 23,
            'on_expander': True,
        },
        'estop': {
            'name': 'estop',
            'pins': {'1': 34, '2': 35},
        },
        'bms': {
            'name': 'bms',
            'on_expander': True,
            'rx_pin': 26,
            'tx_pin': 27,
            'baud': 9600,
            'num': 2,
        },
        'battery_control': {
            'name': 'battery_control',
            'on_expander': True,
            'reset_pin': 15,
            'status_pin': 13,
        },
    },
    'u3': {
        'params': {
            'motor_gear_ratio': 12.52,
            'thooth_count': 17,
            'pitch': 0.041,
            'wheel_distance': 0.47,
            'work_x_chop': -0.0715,
            'work_x_drill': 0.061,
            'drill_radius': 0.025,
            'chop_radius': 0.07,
        },
        'robot_brain': {
            'flash_params': ['orin']
        },
        'bluetooth': {
            'name': 'uckerbot-u3',
        },
        'serial': {
            'name': 'serial',
            'rx_pin': 26,
            'tx_pin': 27,
            'baud': 115200,
            'num': 1,
        },
        'expander': {
            'name': 'p0',
            'boot': 25,
            'enable': 14,
        },
        'can': {
            'name': 'can',
            'on_expander': False,
            'rx_pin': 32,
            'tx_pin': 33,
            'baud': 1_000_000,
        },
        'wheels': {
            'version': 'double_wheels',
            'name': 'wheels',
            'left_back_can_address': 0x000,
            'left_front_can_address': 0x100,
            'right_back_can_address': 0x200,
            'right_front_can_address': 0x300,
            'is_left_reversed': True,
            'is_right_reversed': False,
        },
        'y_axis': {
            'version': 'chain_axis',
            'name': 'chain_axis',
            'motor_on_expander': False,
            'end_stops_on_expander': True,
            'step_pin': 13,
            'dir_pin': 4,
            'alarm_pin': 36,
            'ref_t_pin': 35,
        },
        'z_axis': {
            'version': 'z_axis_v2',
            'name': 'z_axis',
            'step_pin': 33,
            'dir_pin': 4,
            'alarm_pin': 32,
            'ref_t_pin': 12,
            'end_b_pin': 25,
            'motor_on_expander': True,
            'end_stops_on_expander': True,
            'ref_t_inverted': False,
            'end_b_inverted':  False,
            'ccw': False,
        },
        'flashlight': {
            'version': 'flashlight_v2',
            'name': 'flashlight',
            'front_pin': 23,
            'back_pin': 22,
            'on_expander': True,
        },
        'estop': {
            'name': 'estop',
            'pins': {'1': 34, '2': 35},
        },
        'bms': {
            'name': 'bms',
            'on_expander': True,
            'rx_pin': 26,
            'tx_pin': 27,
            'baud': 9600,
            'num': 2,
        },
        'battery_control': {
            'name': 'battery_control',
            'on_expander': True,
            'reset_pin': 15,
            'status_pin': 13,
        },
    },


    'u4': {
        'params': {
            'motor_gear_ratio': 12.52,
            'thooth_count': 17,
            'pitch': 0.041,
            'wheel_distance': 0.47,
            'work_x': 0.118,
            'drill_radius': 0.025,
        },
        'robot_brain': {
            'flash_params': ['orin']
        },
        'bluetooth': {
            'name': 'uckerbot-u4',
        },
        'serial': {
            'name': 'serial',
            'rx_pin': 26,
            'tx_pin': 27,
            'baud': 115200,
            'num': 1,
        },
        'expander': {
            'name': 'p0',
            'boot': 25,
            'enable': 14,
        },
        'can': {
            'name': 'can',
            'on_expander': False,
            'rx_pin': 32,
            'tx_pin': 33,
            'baud': 1_000_000,
        },
        'wheels': {
            'version': 'double_wheels',
            'name': 'wheels',
            'left_back_can_address': 0x000,
            'left_front_can_address': 0x100,
            'right_back_can_address': 0x200,
            'right_front_can_address': 0x300,
            'is_left_reversed': False,
            'is_right_reversed': True,
        },
        'y_axis': {
            'version': 'y_axis_tornado',
            'name': 'y_axis',
            'max_speed': 80_000,
            'min_position': -0.12,
            'max_position': 0.12,
            'axis_offset': 0.123,
            'steps_per_m': 666.67 * 1000,
            'step_pin': 19,
            'dir_pin': 18,
            'alarm_pin': 35,
            'end_r_pin': 13,
            'end_l_pin': 36,
            'motor_on_expander': False,
            'end_stops_on_expander': True,
        },
        'z_axis': {
            'version': 'tornado',
            'name': 'tornado',
            'min_position': -0.12,
            'z_can_address': 0x400,
            'turn_can_address': 0x500,
            'm_per_tick': 0.01,
            'end_top_pin': 32,
            'end_bottom_pin': 5,
            'ref_motor_pin': 33,
            'ref_gear_pin': 4,
            'ref_t_pin': 35,
            'ref_b_pin': 18,
            'motors_on_expander': False,
            'end_stops_on_expander': True,
            'is_z_reversed': False,
            'is_turn_reversed': False,
            'speed_limit': 1,
            'current_limit': 20,
        },
        'flashlight': {
            'version': 'flashlight_pwm',
            'name': 'flashlight',
            'pin': 2,
            'on_expander': True,
            'rated_voltage': 23.0,
        },
        'estop': {
            'name': 'estop',
            'pins': {'1': 34, '2': 35},
        },
        'bms': {
            'name': 'bms',
            'on_expander': True,
            'rx_pin': 26,
            'tx_pin': 27,
            'baud': 9600,
            'num': 2,
        },
        'battery_control': {
            'name': 'battery_control',
            'on_expander': True,
            'reset_pin': 15,
            'status_pin': 13,
        },
        'bumper': {
            'name': 'bumper',
            'on_expander': True,
            'pins': {'front_top': 22, 'front_bottom': 12, 'back': 25, 'empty': 23},
        },
        'status_control': {
            'name': 'status_control',
        },
    },


    'ff3': {
        'params': {
            'motor_gear_ratio': 12.52,
            'thooth_count': 17,
            'pitch': 0.041,
            'wheel_distance': 0.47,
            'work_x': 0.118,
            'drill_radius': 0.025,
        },
        'robot_brain': {
            'flash_params': [],
        },
        'bluetooth': {
            'name': 'fieldfriend-ff3',
        },
        'serial': {
            'name': 'serial',
            'rx_pin': 26,
            'tx_pin': 27,
            'baud': 115200,
            'num': 1,
        },
        'expander': {
            'name': 'p0',
            'boot': 25,
            'enable': 14,
        },
        'can': {
            'name': 'can',
            'on_expander': False,
            'rx_pin': 32,
            'tx_pin': 33,
            'baud': 1_000_000,
        },
        'wheels': {
            'version': 'wheels',
            'name': 'wheels',
            'left_can_address': 0x000,
            'right_can_address': 0x100,
            'is_left_reversed': False,
            'is_right_reversed': True,
        },
        'y_axis': {
            'version': 'y_axis',
            'name': 'y_axis',
            'motor_on_expander': False,
            'end_stops_on_expander': True,
            'step_pin': 5,
            'dir_pin': 4,
            'alarm_pin': 13,
            'end_l_pin': 21,
            'end_r_pin': 35,
        },
        'z_axis': {
            'version': 'z_axis_v2',
            'name': 'z_axis',
            'step_pin': 5,
            'dir_pin': 4,
            'alarm_pin': 33,
            'ref_t_pin': 25,
            'end_b_pin': 22,
            'motor_on_expander': True,
            'end_stops_on_expander': True,
            'ref_t_inverted': True,
            'end_b_inverted':  False,
            'ccw': True,

        },
        'flashlight': {
            'version': 'none',
        },
        'estop': {
            'name': 'estop',
            'pins': {'1': 34, '2': 35},
        },
        'bms': {
            'name': 'bms',
            'on_expander': True,
            'rx_pin': 26,
            'tx_pin': 27,
            'baud': 9600,
            'num': 2,
        },
        'battery_control': {
            'name': 'battery_control',
            'on_expander': True,
            'reset_pin': 15,
            'status_pin': 13,
        },
    },
}
