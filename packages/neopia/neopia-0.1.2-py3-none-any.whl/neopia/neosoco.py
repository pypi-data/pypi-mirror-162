# Part of the ROBOID project - https://roboticsware.uz
# Copyright (C) 2022 RoboticsWare (neopia.uz@gmail.com)
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General
# Public License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA


import time

from neopia.runner import Runner
from neopia.util import Util
from neopia.model import Robot
from neopia.mode import Mode


class Neosoco(Robot):
    ID = "kr.neobot.physical.neosoco"

    OUTPUT_1    = 0x00400000
    OUTPUT_2    = 0x00400001
    OUTPUT_3    = 0x00400002
    INPUT_1     = 0x00400003
    INPUT_2     = 0x00400004
    INPUT_3     = 0x00400005
    REMOCTL     = 0x00400006
    BATTERY     = 0x00400007
    LEFT_MOTOR  = 0x00400008
    RIGHT_MOTOR = 0x00400009

    LED_OFF = 0
    LED_BLUE = 1
    LED_GREEN = 2
    LED_CYAN = 3
    LED_SKY_BLUE = 3
    LED_RED = 4
    LED_MAGENTA = 5
    LED_PURPLE = 5
    LED_YELLOW = 6
    LED_WHITE = 7

    COLOR_NAME_OFF = "off"
    COLOR_NAME_RED = "red"
    COLOR_NAME_YELLOW = "yellow"
    COLOR_NAME_GREEN = "green"
    COLOR_NAME_SKY_BLUE = "sky blue"
    COLOR_NAME_BLUE = "blue"
    COLOR_NAME_PURPLE = "purple"
    COLOR_NAME_WHITE = "white"

    LINE_TRACER_MODE_OFF = 0
    LINE_TRACER_MODE_BLACK_LEFT_SENSOR = 1
    LINE_TRACER_MODE_BLACK_RIGHT_SENSOR = 2
    LINE_TRACER_MODE_BLACK_BOTH_SENSORS = 3
    LINE_TRACER_MODE_BLACK_TURN_LEFT = 4
    LINE_TRACER_MODE_BLACK_TURN_RIGHT = 5
    LINE_TRACER_MODE_BLACK_MOVE_FORWARD = 6
    LINE_TRACER_MODE_BLACK_UTURN = 7
    LINE_TRACER_MODE_WHITE_LEFT_SENSOR = 8
    LINE_TRACER_MODE_WHITE_RIGHT_SENSOR = 9
    LINE_TRACER_MODE_WHITE_BOTH_SENSORS = 10
    LINE_TRACER_MODE_WHITE_TURN_LEFT = 11
    LINE_TRACER_MODE_WHITE_TURN_RIGHT = 12
    LINE_TRACER_MODE_WHITE_MOVE_FORWARD = 13
    LINE_TRACER_MODE_WHITE_UTURN = 14

    IO_MODE_ANALOG_INPUT = 0
    IO_MODE_DIGITAL_INPUT = 1
    IO_MODE_SERVO_OUTPUT = 8
    IO_MODE_PWM_OUTPUT = 9
    IO_MODE_DIGITAL_OUTPUT = 10

    IO_MODE_NAME_ANALOG_INPUT = "analog input"
    IO_MODE_NAME_DIGITAL_INPUT = "digital input"
    IO_MODE_NAME_SERVO_OUTPUT = "servo output"
    IO_MODE_NAME_PWM_OUTPUT = "pwm output"
    IO_MODE_NAME_DIGITAL_OUTPUT = "digital output"

    NOTE_OFF = 0
    NOTE_A_0 = 1
    NOTE_A_SHARP_0 = 2
    NOTE_B_FLAT_0 = 2
    NOTE_B_0 = 3
    NOTE_C_1 = 4
    NOTE_C_SHARP_1 = 5
    NOTE_D_FLAT_1 = 5
    NOTE_D_1 = 6
    NOTE_D_SHARP_1 = 7
    NOTE_E_FLAT_1 = 7
    NOTE_E_1 = 8
    NOTE_F_1 = 9
    NOTE_F_SHARP_1 = 10
    NOTE_G_FLAT_1 = 10
    NOTE_G_1 = 11
    NOTE_G_SHARP_1 = 12
    NOTE_A_FLAT_1 = 12
    NOTE_A_1 = 13
    NOTE_A_SHARP_1 = 14
    NOTE_B_FLAT_1 = 14
    NOTE_B_1 = 15
    NOTE_C_2 = 16
    NOTE_C_SHARP_2 = 17
    NOTE_D_FLAT_2 = 17
    NOTE_D_2 = 18
    NOTE_D_SHARP_2 = 19
    NOTE_E_FLAT_2 = 19
    NOTE_E_2 = 20
    NOTE_F_2 = 21
    NOTE_F_SHARP_2 = 22
    NOTE_G_FLAT_2 = 22
    NOTE_G_2 = 23
    NOTE_G_SHARP_2 = 24
    NOTE_A_FLAT_2 = 24
    NOTE_A_2 = 25
    NOTE_A_SHARP_2 = 26
    NOTE_B_FLAT_2 = 26
    NOTE_B_2 = 27
    NOTE_C_3 = 28
    NOTE_C_SHARP_3 = 29
    NOTE_D_FLAT_3 = 29
    NOTE_D_3 = 30
    NOTE_D_SHARP_3 = 31
    NOTE_E_FLAT_3 = 31
    NOTE_E_3 = 32
    NOTE_F_3 = 33
    NOTE_F_SHARP_3 = 34
    NOTE_G_FLAT_3 = 34
    NOTE_G_3 = 35
    NOTE_G_SHARP_3 = 36
    NOTE_A_FLAT_3 = 36
    NOTE_A_3 = 37
    NOTE_A_SHARP_3 = 38
    NOTE_B_FLAT_3 = 38
    NOTE_B_3 = 39
    NOTE_C_4 = 40
    NOTE_C_SHARP_4 = 41
    NOTE_D_FLAT_4 = 41
    NOTE_D_4 = 42
    NOTE_D_SHARP_4 = 43
    NOTE_E_FLAT_4 = 43
    NOTE_E_4 = 44
    NOTE_F_4 = 45
    NOTE_F_SHARP_4 = 46
    NOTE_G_FLAT_4 = 46
    NOTE_G_4 = 47
    NOTE_G_SHARP_4 = 48
    NOTE_A_FLAT_4 = 48
    NOTE_A_4 = 49
    NOTE_A_SHARP_4 = 50
    NOTE_B_FLAT_4 = 50
    NOTE_B_4 = 51
    NOTE_C_5 = 52
    NOTE_C_SHARP_5 = 53
    NOTE_D_FLAT_5 = 53
    NOTE_D_5 = 54
    NOTE_D_SHARP_5 = 55
    NOTE_E_FLAT_5 = 55
    NOTE_E_5 = 56
    NOTE_F_5 = 57
    NOTE_F_SHARP_5 = 58
    NOTE_G_FLAT_5 = 58
    NOTE_G_5 = 59
    NOTE_G_SHARP_5 = 60
    NOTE_A_FLAT_5 = 60
    NOTE_A_5 = 61
    NOTE_A_SHARP_5 = 62
    NOTE_B_FLAT_5 = 62
    NOTE_B_5 = 63
    NOTE_C_6 = 64
    NOTE_C_SHARP_6 = 65
    NOTE_D_FLAT_6 = 65
    NOTE_D_6 = 66
    NOTE_D_SHARP_6 = 67
    NOTE_E_FLAT_6 = 67
    NOTE_E_6 = 68
    NOTE_F_6 = 69
    NOTE_F_SHARP_6 = 70
    NOTE_G_FLAT_6 = 70
    NOTE_G_6 = 71
    NOTE_G_SHARP_6 = 72
    NOTE_A_FLAT_6 = 72
    NOTE_A_6 = 73
    NOTE_A_SHARP_6 = 74
    NOTE_B_FLAT_6 = 74
    NOTE_B_6 = 75
    NOTE_C_7 = 76
    NOTE_C_SHARP_7 = 77
    NOTE_D_FLAT_7 = 77
    NOTE_D_7 = 78
    NOTE_D_SHARP_7 = 79
    NOTE_E_FLAT_7 = 79
    NOTE_E_7 = 80
    NOTE_F_7 = 81
    NOTE_F_SHARP_7 = 82
    NOTE_G_FLAT_7 = 82
    NOTE_G_7 = 83
    NOTE_G_SHARP_7 = 84
    NOTE_A_FLAT_7 = 84
    NOTE_A_7 = 85
    NOTE_A_SHARP_7 = 86
    NOTE_B_FLAT_7 = 86
    NOTE_B_7 = 87
    NOTE_C_8 = 88

    NOTE_NAME_C = "C"
    NOTE_NAME_C_SHARP = "C#"
    NOTE_NAME_D_FLAT = "Db"
    NOTE_NAME_D = "D"
    NOTE_NAME_D_SHARP = "D#"
    NOTE_NAME_E_FLAT = "Eb"
    NOTE_NAME_E = "E"
    NOTE_NAME_F = "F"
    NOTE_NAME_F_SHARP = "F#"
    NOTE_NAME_G_FLAT = "Gb"
    NOTE_NAME_G = "G"
    NOTE_NAME_G_SHARP = "G#"
    NOTE_NAME_A_FLAT = "Ab"
    NOTE_NAME_A = "A"
    NOTE_NAME_A_SHARP = "A#"
    NOTE_NAME_B_FLAT = "Bb"
    NOTE_NAME_B = "B"

    TILT_FORWARD = 1
    TILT_BACKWARD = -1
    TILT_LEFT = 2
    TILT_RIGHT = -2
    TILT_FLIP = 3
    TILT_NOT = -3

    BATTERY_NORMAL = 2
    BATTERY_LOW = 1
    BATTERY_EMPTY = 0

    _COLORS = {
        "off": LED_OFF,
        "red": LED_RED,
        "yellow": LED_YELLOW,
        "green": LED_GREEN,
        "sky_blue": LED_CYAN,
        "skyblue": LED_CYAN,
        "sky blue": LED_CYAN,
        "blue": LED_BLUE,
        "purple": LED_MAGENTA,
        "white": LED_WHITE
    }
    _NOTES = {
        "c": NOTE_C_1,
        "c#": NOTE_C_SHARP_1,
        "db": NOTE_D_FLAT_1,
        "d": NOTE_D_1,
        "d#": NOTE_D_SHARP_1,
        "eb": NOTE_E_FLAT_1,
        "e": NOTE_E_1,
        "f": NOTE_F_1,
        "f#": NOTE_F_SHARP_1,
        "gb": NOTE_G_FLAT_1,
        "g": NOTE_G_1,
        "g#": NOTE_G_SHARP_1,
        "ab": NOTE_A_FLAT_1,
        "a": NOTE_A_1,
        "a#": NOTE_A_SHARP_1,
        "bb": NOTE_B_FLAT_1,
        "b": NOTE_B_1
    }
    _IO_MODES = {
        "analog_input": IO_MODE_ANALOG_INPUT,
        "analog input": IO_MODE_ANALOG_INPUT,
        "digital_input": IO_MODE_DIGITAL_INPUT,
        "digital input": IO_MODE_DIGITAL_INPUT,
        "servo_output": IO_MODE_SERVO_OUTPUT,
        "servo output": IO_MODE_SERVO_OUTPUT,
        "pwm_output": IO_MODE_PWM_OUTPUT,
        "pwm output": IO_MODE_PWM_OUTPUT,
        "digital_output": IO_MODE_DIGITAL_OUTPUT,
        "digital output": IO_MODE_DIGITAL_OUTPUT
    }
    _MOTOR_PERCENT_CVT = { 
        '100': 15,
        '90': 14,
        '80': 13,
        '70': 12,
        '60': 10,
        '50': 9,
        '40': 7,
        '30': 5,
        '20': 3,
        '10': 2,
        '0': 0
    }
    _MOTOR_DIR = { 
        'forward': 16,
        'backward': 32
    }
    _robots = {}

    def __init__(self, index=0, port_name=None):
        if isinstance(index, str):
            index = 0
            port_name = index
        if index in Neosoco._robots:
            robot = Neosoco._robots[index]
            if robot: robot.dispose()
        Neosoco._robots[index] = self
        super(Neosoco, self).__init__(Neosoco.ID, "Neosoco", index)
        self._bpm = 60
        self._init(port_name)

    def dispose(self):
        Neosoco._robots[self.get_index()] = None
        self._roboid._dispose()
        Runner.unregister_robot(self)

    def reset(self):
        self._bpm = 60
        self._roboid._reset()

    def _init(self, port_name):
        if Mode.is_link_mode():
            from neopia.neosoco_neobot import NeosocoLinkNeobot
            self._roboid = NeosocoLinkNeobot(self.get_index())
        else:
            from neopia.neosoco_neobot import NeosocoNeobot
            self._roboid = NeosocoNeobot(self.get_index())
        self._add_roboid(self._roboid)
        Runner.register_robot(self)
        Runner.start()
        self._roboid._init(port_name)

    def find_device_by_id(self, device_id):
        return self._roboid.find_device_by_id(device_id)

    def _request_motoring_data(self):
        self._roboid._request_motoring_data()

    def _update_sensory_device_state(self):
        self._roboid._update_sensory_device_state()

    def _update_motoring_device_state(self):
        self._roboid._update_motoring_device_state()

    def _notify_sensory_device_data_changed(self):
        self._roboid._notify_sensory_device_data_changed()

    def _notify_motoring_device_data_changed(self):
        self._roboid._notify_motoring_device_data_changed()

    def set_value(self, port: str, value: int):
        if isinstance(port, str) and isinstance(value, int):
            if port.lower() =='out1':
                self.write(Neosoco.OUTPUT_1, Util.round(value)) 
            elif port.lower() =='out2':
                self.write(Neosoco.OUTPUT_2, Util.round(value)) 
            elif port.lower() =='out3':
                self.write(Neosoco.OUTPUT_3, Util.round(value)) 
            elif port.lower() =='all':
                self.write(Neosoco.OUTPUT_1, Util.round(value)) 
                self.write(Neosoco.OUTPUT_2, Util.round(value)) 
                self.write(Neosoco.OUTPUT_3, Util.round(value))
            else:
                Util.print_error('Wrong value of port')
                raise ValueError
        else:
            raise TypeError

    def get_value(self, port: str):
        if isinstance(port, str):
            if port.lower() =='in1':
                return self.read(Neosoco.INPUT_1)
            elif port.lower() =='in2':
                return self.read(Neosoco.INPUT_2)
            elif port.lower() =='in3':
                return self.read(Neosoco.INPUT_3)
            elif port.lower() =='remo':
                return self.read(Neosoco.REMOCTL)
            elif port.lower() =='bat':
                return self.read(Neosoco.BATTERY)
            else:
                Util.print_error('Wrong value of port')
                raise ValueError
        else:
            raise TypeError

    def led_on(self, port: str, brightness: str):
        try:
            cvt_dic = { 
                '100': 255,
                '90': 230,
                '80': 204,
                '70': 179,
                '60': 153,
                '50': 128,
                '40': 102,
                '30': 77,
                '20': 51,
                '10': 26
            }
            cvt_val = cvt_dic[brightness]
        except KeyError:
            Util.print_error('Wrong value of percentage')
            raise ValueError
        if isinstance(port, str):
            if port.lower() =='out1':
                self.write(Neosoco.OUTPUT_1, cvt_val) 
            elif port.lower() =='out2':
                self.write(Neosoco.OUTPUT_2, cvt_val) 
            elif port.lower() =='out3':
                self.write(Neosoco.OUTPUT_3, cvt_val) 
            elif port.lower() =='all':
                self.write(Neosoco.OUTPUT_1, cvt_val) 
                self.write(Neosoco.OUTPUT_2, cvt_val) 
                self.write(Neosoco.OUTPUT_3, cvt_val)
            else:
                Util.print_error('Wrong value of port')
                raise ValueError
        else:
            raise TypeError

    def motor_move(self, direction: str):
        if isinstance(direction, str):
            if direction.lower() =='forward':
                self.write(Neosoco.LEFT_MOTOR, self._MOTOR_DIR['forward']+self._MOTOR_PERCENT_CVT['60'])
                self.write(Neosoco.RIGHT_MOTOR, self._MOTOR_DIR['forward']+self._MOTOR_PERCENT_CVT['60'])
            elif direction.lower() =='backward':
                self.write(Neosoco.LEFT_MOTOR, self._MOTOR_DIR['backward']+self._MOTOR_PERCENT_CVT['60'])
                self.write(Neosoco.RIGHT_MOTOR, self._MOTOR_DIR['backward']+self._MOTOR_PERCENT_CVT['60'])
            elif direction.lower() =='left':
                self.write(Neosoco.LEFT_MOTOR, self._MOTOR_DIR['backward']+self._MOTOR_PERCENT_CVT['60'])
                self.write(Neosoco.RIGHT_MOTOR, self._MOTOR_DIR['forward']+self._MOTOR_PERCENT_CVT['60'])
            elif direction.lower() =='right':
                self.write(Neosoco.LEFT_MOTOR, self._MOTOR_DIR['forward']+self._MOTOR_PERCENT_CVT['60'])
                self.write(Neosoco.RIGHT_MOTOR, self._MOTOR_DIR['backward']+self._MOTOR_PERCENT_CVT['60'])
            elif direction.lower() =='stop':
                self.write(Neosoco.LEFT_MOTOR, 0)
                self.write(Neosoco.RIGHT_MOTOR, 0)
            else:
                Util.print_error('Wrong value of direction')
                raise ValueError
        else:
            raise TypeError
        time.sleep(0.1) # Since brocast from cotroller is per 100ms

    def wheels(self, left_velocity, right_velocity=None):
        self.write(Neosoco.LINE_TRACER_MODE, Neosoco.LINE_TRACER_MODE_OFF)
        if isinstance(left_velocity, (int, float)):
            self.write(Neosoco.LEFT_WHEEL, Util.round(left_velocity))
        if isinstance(right_velocity, (int, float)):
            self.write(Neosoco.RIGHT_WHEEL, Util.round(right_velocity))
        else:
            if isinstance(left_velocity, (int, float)):
                self.write(Neosoco.RIGHT_WHEEL, Util.round(left_velocity))

    def left_wheel(self, velocity):
        self.write(Neosoco.LINE_TRACER_MODE, Neosoco.LINE_TRACER_MODE_OFF)
        if isinstance(velocity, (int, float)):
            self.write(Neosoco.LEFT_WHEEL, Util.round(velocity))

    def right_wheel(self, velocity):
        self.write(Neosoco.LINE_TRACER_MODE, Neosoco.LINE_TRACER_MODE_OFF)
        if isinstance(velocity, (int, float)):
            self.write(Neosoco.RIGHT_WHEEL, Util.round(velocity))

    def stop(self):
        self.write(Neosoco.LINE_TRACER_MODE, Neosoco.LINE_TRACER_MODE_OFF)
        self.write(Neosoco.LEFT_WHEEL, 0)
        self.write(Neosoco.RIGHT_WHEEL, 0)

    def _motion_sec(self, sec, left_velocity, right_velocity):
        self.write(Neosoco.LINE_TRACER_MODE, Neosoco.LINE_TRACER_MODE_OFF)
        if sec < 0:
            sec = -sec
            left_velocity = -left_velocity
            right_velocity = -right_velocity
        if sec > 0:
            self.write(Neosoco.LEFT_WHEEL, Util.round(left_velocity))
            self.write(Neosoco.RIGHT_WHEEL, Util.round(right_velocity))
            Runner.wait(sec * 1000)
        self.write(Neosoco.LEFT_WHEEL, 0)
        self.write(Neosoco.RIGHT_WHEEL, 0)

    def move_forward(self, sec=1, velocity=30):
        if isinstance(sec, (int, float)) and isinstance(velocity, (int, float)):
            self._motion_sec(sec, velocity, velocity)

    def move_backward(self, sec=1, velocity=30):
        if isinstance(sec, (int, float)) and isinstance(velocity, (int, float)):
            self._motion_sec(sec, -velocity, -velocity)

    def turn_left(self, sec=1, velocity=30):
        if isinstance(sec, (int, float)) and isinstance(velocity, (int, float)):
            self._motion_sec(sec, -velocity, velocity)

    def turn_right(self, sec=1, velocity=30):
        if isinstance(sec, (int, float)) and isinstance(velocity, (int, float)):
            self._motion_sec(sec, velocity, -velocity)

    def _evaluate_line_tracer(self):
        return self.e(Neosoco.LINE_TRACER_STATE) and self.read(Neosoco.LINE_TRACER_STATE) == 0x40

    def line_tracer_mode(self, mode):
        self.write(Neosoco.LEFT_WHEEL, 0)
        self.write(Neosoco.RIGHT_WHEEL, 0)
        if isinstance(mode, (int, float)):
            mode = int(mode)
            self.write(Neosoco.LINE_TRACER_MODE, mode)
            if (mode >= 4 and mode <= 7) or (mode >= 11 and mode <= 14):
                Runner.wait_until(self._evaluate_line_tracer)
                self.write(Neosoco.LINE_TRACER_MODE, Neosoco.LINE_TRACER_MODE_OFF)

    def line_left(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_BLACK_LEFT_SENSOR)

    def line_right(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_BLACK_RIGHT_SENSOR)

    def line_both(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_BLACK_BOTH_SENSORS)

    def cross_forward(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_BLACK_MOVE_FORWARD)

    def cross_left(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_BLACK_TURN_LEFT)

    def cross_right(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_BLACK_TURN_RIGHT)

    def cross_uturn(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_BLACK_UTURN)

    def white_line_left(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_WHITE_LEFT_SENSOR)

    def white_line_right(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_WHITE_RIGHT_SENSOR)

    def white_line_both(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_WHITE_BOTH_SENSORS)

    def white_cross_forward(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_WHITE_MOVE_FORWARD)

    def white_cross_left(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_WHITE_TURN_LEFT)

    def white_cross_right(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_WHITE_TURN_RIGHT)

    def white_cross_uturn(self):
        self.line_tracer_mode(Neosoco.LINE_TRACER_MODE_WHITE_UTURN)

    def line_speed(self, speed):
        if isinstance(speed, (int, float)):
            self.write(Neosoco.LINE_TRACER_SPEED, Util.round(speed))

    def line_tracer_speed(self, speed):
        self.line_speed(speed)

    def _evaluate_board_forward(self):
        if self._board_state == 1:
            if self._board_count < 2:
                left_floor = self.read(Neosoco.LEFT_FLOOR)
                right_floor = self.read(Neosoco.RIGHT_FLOOR)
                if left_floor < 50 and right_floor < 50:
                    self._board_count += 1
                else:
                    self._board_count = 0
                diff = left_floor - right_floor
                self.write(Neosoco.LEFT_WHEEL, Util.round(45 + diff * 0.25))
                self.write(Neosoco.RIGHT_WHEEL, Util.round(45 - diff * 0.25))
            else:
                self._board_count = 0
                self._board_state = 2
        elif self._board_state == 2:
            if self._board_count < 10:
                self._board_count += 1
                diff = self.read(Neosoco.LEFT_FLOOR) - self.read(Neosoco.RIGHT_FLOOR)
                self.write(Neosoco.LEFT_WHEEL, Util.round(45 + diff * 0.25))
                self.write(Neosoco.RIGHT_WHEEL, Util.round(45 - diff * 0.25))
            else:
                self.write(Neosoco.LEFT_WHEEL, 0)
                self.write(Neosoco.RIGHT_WHEEL, 0)
                return True
        return False

    def board_forward(self):
        self.write(Neosoco.LINE_TRACER_MODE, Neosoco.LINE_TRACER_MODE_OFF)
        self.write(Neosoco.LEFT_WHEEL, 45)
        self.write(Neosoco.RIGHT_WHEEL, 45)
        self._board_count = 0
        self._board_state = 1
        Runner.wait_until(self._evaluate_board_forward)

    def _evaluate_board_left(self):
        state = self._board_state
        if state == 1:
            if self._board_count < 2:
                if self.read(Neosoco.LEFT_FLOOR) > 50:
                    self._board_count += 1
            else:
                self._board_count = 0
                self._board_state = 2
        elif state == 2:
            if self.read(Neosoco.LEFT_FLOOR) < 20:
                self._board_state = 3
        elif state == 3:
            if self._board_count < 2:
                if self.read(Neosoco.LEFT_FLOOR) < 20:
                    self._board_count += 1
            else:
                self._board_count = 0
                self._board_state = 4
        elif state == 4:
            if self.read(Neosoco.LEFT_FLOOR) > 50:
                self._board_state = 5
        elif state == 5:
            diff = self.read(Neosoco.LEFT_FLOOR) - self.read(Neosoco.RIGHT_FLOOR)
            if diff > -15:
                self.write(Neosoco.LEFT_WHEEL, 0)
                self.write(Neosoco.RIGHT_WHEEL, 0)
                return True
            else:
                self.write(Neosoco.LEFT_WHEEL, Util.round(diff * 0.5))
                self.write(Neosoco.RIGHT_WHEEL, -Util.round(diff * 0.5))
        return False

    def board_left(self):
        self.write(Neosoco.LINE_TRACER_MODE, Neosoco.LINE_TRACER_MODE_OFF)
        self.write(Neosoco.LEFT_WHEEL, -45)
        self.write(Neosoco.RIGHT_WHEEL, 45)
        self._board_count = 0
        self._board_state = 1
        Runner.wait_until(self._evaluate_board_left)

    def _evaluate_board_right(self):
        state = self._board_state
        if state == 1:
            if self._board_count < 2:
                if self.read(Neosoco.RIGHT_FLOOR) > 50:
                    self._board_count += 1
            else:
                self._board_count = 0
                self._board_state = 2
        elif state == 2:
            if self.read(Neosoco.RIGHT_FLOOR) < 20:
                self._board_state = 3
        elif state == 3:
            if self._board_count < 2:
                if self.read(Neosoco.RIGHT_FLOOR) < 20:
                    self._board_count += 1
            else:
                self._board_count = 0
                self._board_state = 4
        elif state == 4:
            if self.read(Neosoco.RIGHT_FLOOR) > 50:
                self._board_state = 5
        elif state == 5:
            diff = self.read(Neosoco.RIGHT_FLOOR) - self.read(Neosoco.LEFT_FLOOR)
            if diff > -15:
                self.write(Neosoco.LEFT_WHEEL, 0)
                self.write(Neosoco.RIGHT_WHEEL, 0)
                return True
            else:
                self.write(Neosoco.LEFT_WHEEL, -Util.round(diff * 0.5))
                self.write(Neosoco.RIGHT_WHEEL, Util.round(diff * 0.5))
        return False

    def board_right(self):
        self.write(Neosoco.LINE_TRACER_MODE, Neosoco.LINE_TRACER_MODE_OFF)
        self.write(Neosoco.LEFT_WHEEL, 45)
        self.write(Neosoco.RIGHT_WHEEL, -45)
        self._board_count = 0
        self._board_state = 1
        Runner.wait_until(self._evaluate_board_right)

    def leds(self, left_color, right_color=None):
        if isinstance(left_color, (int, float)):
            self.write(Neosoco.LEFT_LED, int(left_color))
        elif isinstance(left_color, str):
            tmp = left_color.lower()
            if tmp in Neosoco._COLORS:
                left_color = Neosoco._COLORS[tmp]
                self.write(Neosoco.LEFT_LED, left_color)
        if isinstance(right_color, (int, float)):
            self.write(Neosoco.RIGHT_LED, int(right_color))
        elif isinstance(right_color, str):
            tmp = right_color.lower()
            if tmp in Neosoco._COLORS:
                right_color = Neosoco._COLORS[tmp]
                self.write(Neosoco.RIGHT_LED, right_color)
        else:
            if isinstance(left_color, (int, float)):
                self.write(Neosoco.RIGHT_LED, int(left_color))

    def left_led(self, color):
        if isinstance(color, (int, float)):
            self.write(Neosoco.LEFT_LED, int(color))
        elif isinstance(color, str):
            tmp = color.lower()
            if tmp in Neosoco._COLORS:
                self.write(Neosoco.LEFT_LED, Neosoco._COLORS[tmp])

    def right_led(self, color):
        if isinstance(color, (int, float)):
            self.write(Neosoco.RIGHT_LED, int(color))
        elif isinstance(color, str):
            tmp = color.lower()
            if tmp in Neosoco._COLORS:
                self.write(Neosoco.RIGHT_LED, Neosoco._COLORS[tmp])

    def beep(self):
        self.write(Neosoco.NOTE, Neosoco.NOTE_OFF)
        self.write(Neosoco.BUZZER, 440)
        Runner.wait(100)
        self.write(Neosoco.BUZZER, 0)
        Runner.wait(100)

    def buzzer(self, hz):
        self.write(Neosoco.NOTE, Neosoco.NOTE_OFF)
        if isinstance(hz, (int, float)):
            self.write(Neosoco.BUZZER, hz)

    def tempo(self, bpm):
        if isinstance(bpm, (int, float)):
            if bpm > 0:
                self._bpm = bpm

    def note(self, pitch, beats=None):
        self.write(Neosoco.BUZZER, 0)
        if isinstance(pitch, str) and len(pitch) > 0:
            tmp = pitch.lower()
            if tmp == "off":
                pitch = 0
            else:
                octave = 4
                try:
                    octave = int(tmp[-1])
                    tmp = tmp[:-1]
                except ValueError:
                    pass
                if tmp in Neosoco._NOTES:
                    pitch = Neosoco._NOTES[tmp] + (octave - 1) * 12
        if isinstance(pitch, (int, float)):
            pitch = int(pitch)
            if isinstance(beats, (int, float)):
                bpm = self._bpm
                if beats > 0 and bpm > 0:
                    if pitch == 0:
                        self.write(Neosoco.NOTE, Neosoco.NOTE_OFF)
                        Runner.wait(beats * 60 * 1000.0 / bpm)
                    elif pitch > 0:
                        timeout = beats * 60 * 1000.0 / bpm
                        tail = 0
                        if timeout > 100:
                            tail = 100
                        self.write(Neosoco.NOTE, pitch)
                        Runner.wait(timeout - tail)
                        self.write(Neosoco.NOTE, Neosoco.NOTE_OFF)
                        if tail > 0:
                            Runner.wait(tail)
                else:
                    self.write(Neosoco.NOTE, Neosoco.NOTE_OFF)
            elif pitch >= 0:
                self.write(Neosoco.NOTE, pitch)

    def io_mode_a(self, mode):
        if isinstance(mode, (int, float)):
            self.write(Neosoco.IO_MODE_A, int(mode))
        elif isinstance(mode, str):
            tmp = mode.lower()
            if tmp in Neosoco._IO_MODES:
                self.write(Neosoco.IO_MODE_A, Neosoco._IO_MODES[tmp])

    def io_mode_b(self, mode):
        if isinstance(mode, (int, float)):
            self.write(Neosoco.IO_MODE_B, int(mode))
        elif isinstance(mode, str):
            tmp = mode.lower()
            if tmp in Neosoco._IO_MODES:
                self.write(Neosoco.IO_MODE_B, Neosoco._IO_MODES[tmp])

    def output_a(self, value):
        if isinstance(value, (int, float)):
            self.write(Neosoco.OUTPUT_A, Util.round(value))

    def output_b(self, value):
        if isinstance(value, (int, float)):
            self.write(Neosoco.OUTPUT_B, Util.round(value))

    def open_gripper(self):
        self.write(Neosoco.IO_MODE_A, Neosoco.IO_MODE_DIGITAL_OUTPUT)
        self.write(Neosoco.IO_MODE_B, Neosoco.IO_MODE_DIGITAL_OUTPUT)
        self.write(Neosoco.OUTPUT_A, 1)
        self.write(Neosoco.OUTPUT_B, 0)
        Runner.wait(500)

    def close_gripper(self):
        self.write(Neosoco.IO_MODE_A, Neosoco.IO_MODE_DIGITAL_OUTPUT)
        self.write(Neosoco.IO_MODE_B, Neosoco.IO_MODE_DIGITAL_OUTPUT)
        self.write(Neosoco.OUTPUT_A, 0)
        self.write(Neosoco.OUTPUT_B, 1)
        Runner.wait(500)

    def release_gripper(self):
        self.write(Neosoco.IO_MODE_A, Neosoco.IO_MODE_DIGITAL_OUTPUT)
        self.write(Neosoco.IO_MODE_B, Neosoco.IO_MODE_DIGITAL_OUTPUT)
        self.write(Neosoco.OUTPUT_A, 0)
        self.write(Neosoco.OUTPUT_B, 0)

    def signal_strength(self):
        return self.read(Neosoco.SIGNAL_STRENGTH)

    def left_proximity(self):
        return self.read(Neosoco.LEFT_PROXIMITY)

    def right_proximity(self):
        return self.read(Neosoco.RIGHT_PROXIMITY)

    def left_floor(self):
        return self.read(Neosoco.LEFT_FLOOR)

    def right_floor(self):
        return self.read(Neosoco.RIGHT_FLOOR)

    def acceleration_x(self):
        return self.read(Neosoco.ACCELERATION, 0)

    def acceleration_y(self):
        return self.read(Neosoco.ACCELERATION, 1)

    def acceleration_z(self):
        return self.read(Neosoco.ACCELERATION, 2)

    def light(self):
        return self.read(Neosoco.LIGHT)

    def temperature(self):
        return self.read(Neosoco.TEMPERATURE)

    def input_a(self):
        return self.read(Neosoco.INPUT_A)

    def input_b(self):
        return self.read(Neosoco.INPUT_B)

    def tilt(self):
        return self.read(Neosoco.TILT)

    def battery_state(self):
        return self.read(Neosoco.BATTERY_STATE)