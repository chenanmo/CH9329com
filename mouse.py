from __future__ import annotations

import random
import time
from typing import Literal

from serial import Serial

from ch9329.utils import get_packet

MouseCtrl = Literal["null", "left", "right", "center"]

ctrl_to_hex_mapping: dict[MouseCtrl, bytes] = {
    "null": b"\x00",
    "left": b"\x01",
    "right": b"\x02",
    "center": b"\x04",
}

HEAD = b"\x57\xab"  # 帧头
ADDR = b"\x00"  # 地址
CMD_ABS = b"\x04"  # 绝对命令
CMD_REL = b"\x05"  # 相对命令
LEN_ABS = b"\x07"  # 绝对数据长度
LEN_REL = b"\x05"  # 相对数据长度


class Mouse:
    ser: Serial = None
    screenx: int = None
    screeny: int = None

    def __init__(self, ser, screenx: int, screeny: int):
        """
        鼠标控制
        :param ser: 串口控制器
        :param screenx: 屏幕X 比如1920
        :param screeny: 屏幕Y 比如1080
        """
        self.ser = ser
        self.screenx = screenx
        self.screeny = screeny

    def wheel_int_to_bytes(self, wheel_delta: int):
        """
        将wheel_delta人类可读整数转换为ch9329可读字节
        """
        # 如果为0x00，则表示没有滚动动作
        # 0x01-0x7F，表示向上滚动
        # 0x81-0xFF，表示向下滚动
        if abs(wheel_delta) > 127:
            raise RuntimeError("允许的最大车轮增量为 127。")
        if wheel_delta >= 0:
            return (0x00 + wheel_delta).to_bytes(1)
        else:
            return (0x100 + wheel_delta).to_bytes(1)

    def send_data_absolute(
            self,
            x: int,
            y: int,
            ctrl: MouseCtrl = "null",
            wheel_delta: int = 0,
    ) -> None:
        """绝对移动"""
        # CMD_SEND_MS_ABS_DATA 正好有 7 个字节

        # 第一个字节始终是 0x02
        data = b"\x02"

        # 第二个字节是鼠标按钮值
        data += ctrl_to_hex_mapping[ctrl]

        # 第三和第四个字节是x坐标
        x_cur = (4096 * x) // self.screenx
        data += x_cur.to_bytes(2, byteorder="little")

        # 第五和第六个字节是 y 坐标
        y_cur = (4096 * y) // self.screeny
        data += y_cur.to_bytes(2, byteorder="little")

        # 第七个字节包含车轮数据
        data += self.wheel_int_to_bytes(wheel_delta)

        packet = get_packet(HEAD, ADDR, CMD_ABS, LEN_ABS, data)
        self.ser.write(packet)

    def send_data_relative(self,
                           x: int, y: int, ctrl: MouseCtrl = "null", wheel_delta: int = 0
                           ) -> None:
        """相对移动"""
        # 第一个字节始终为 0x01
        data = b"\x01"

        # 第二个字节是鼠标按钮值
        data += ctrl_to_hex_mapping[ctrl]

        # 第三个字节是x距离
        if x < 0:
            data += (0 - abs(x)).to_bytes(1, byteorder="big", signed=True)
        else:
            data += x.to_bytes(1, byteorder="big", signed=True)

        # 第四个字节是 y 距离
        if y < 0:
            data += (0 - abs(y)).to_bytes(1, byteorder="big", signed=True)
        else:
            data += y.to_bytes(1, byteorder="big", signed=True)

        # 第五个字节包含车轮数据
        data += self.wheel_int_to_bytes(wheel_delta)

        packet = get_packet(HEAD, ADDR, CMD_REL, LEN_REL, data)
        self.ser.write(packet)

    # def move(
    #         self,
    #         x: int,
    #         y: int,
    #         relative: bool = False,
    # ) -> None:
    #     if relative:
    #         self.send_data_relative(x, y, "null")
    #     else:
    #         self.send_data_absolute(x, y, "null", )

    def press(self, button: MouseCtrl = "left") -> None:
        """
        长按鼠标,默认左键
        :param button: "left", "right", "center"
        :return:
        """
        self.send_data_relative(0, 0, button)

    def release(self) -> None:
        """释放鼠标"""
        self.send_data_relative(0, 0, "null")

    def click(self, button: MouseCtrl = "left") -> None:
        """
        单击鼠标,默认左键
        :param button: "left", "right", "center"
        :return:
        """
        self.press(button)
        # 模拟自然行为的 20ms 到 60 毫秒延迟
        time.sleep(random.uniform(0.02, 0.06))
        self.release()

    def wheel(self, wheel: int) -> None:
        """
        滚动鼠标轮子
        :param wheel: 滚动距离
        :return:
        """
        self.send_data_relative(0, 0, wheel_delta=wheel)

    def relative_move(self, x, y):
        """
        相对移动
        :param x: 移动X
        :param y: 移动Y
        :return:
        """
        self.send_data_relative(x, y, "null")

    def absolute_move(self, x, y):
        """
        绝对移动
        :param x: 移动X
        :param y: 移动Y
        :return:
        """
        self.send_data_absolute(x, y, "null")
