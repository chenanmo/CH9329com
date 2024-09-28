from __future__ import annotations

import time
import random
from typing import List
from typing import Literal
from typing import Tuple
from ch9329.exceptions import InvalidKey
from ch9329.exceptions import InvalidModifier
from ch9329.exceptions import TooManyKeysError
from ch9329.hid import HID_MAPPING
from ch9329.utils import get_packet

Modifier = Literal[
    "ctrl",
    "ctrl_left",
    "ctrl_right",
    "shift",
    "shift_left",
    "shift_right",
    "alt",
    "alt_left",
    "alt_right",
    "win",
    "win_left",
    "win_right",
]

MODIFIER_MAP = {
    "ctrl": 0b00000001,
    "ctrl_left": 0b00000001,
    "shift": 0b00000010,
    "shift_left": 0b00000010,
    "alt": 0b00000100,
    "alt_left": 0b00000100,
    "win": 0b00001000,
    "win_left": 0b00001000,
    "ctrl_right": 0b00010000,
    "shift_right": 0b00100000,
    "alt_right": 0b01000000,
    "win_right": 0b10000000,
}

# 将字符转换为数据包
HEAD = b"\x57\xab"  # 帧头
ADDR = b"\x00"  # 地址
CMD = b"\x02"  # 命令
LEN = b"\x08"  # 数据长度


class Keyboard:

    def __init__(self, serial):
        """

        :param serial: 串口控制器
        """
        self.Serial = serial

    def send(
            self, keys: Tuple[str, str, str, str, str, str] = ("", "", "", "", "", ""),
            modifiers: List[Modifier] = [],
    ) -> None:
        """
        发送键盘按键
        :param keys: 按键
        :param modifiers: 控制键
        :return: None
        """
        # CMD_SEND_KB_GENERAL_DATA 数据正好有 8 个字节
        data = b""

        # 第一个字节修饰键，每一位代表1个键
        #
        # BIT0 - ctrl_left
        # BIT1 - shift_left
        # BIT2 - alt_left
        # BIT3 - win_left
        # BIT4 - ctrl_right
        # BIT5 - shift_right
        # BIT6 - alt_right
        # BIT7 - win_right
        modifier = 0x00
        for m in modifiers:
            if m not in MODIFIER_MAP:
                raise InvalidModifier(m)
            modifier |= MODIFIER_MAP[m]
        data += modifier.to_bytes(1, byteorder="little")

        # 第二个字节必须是 0x00
        data += b"\x00"

        # 第三到第八个字节是键
        # 我们最多可以按 6 个按钮
        for key in keys:
            if key not in HID_MAPPING:
                raise InvalidKey(key)
            hid, _ = HID_MAPPING[key]
            data += hid

        # 创建数据包并发送
        packet = get_packet(HEAD, ADDR, CMD, LEN, data)
        self.Serial.write(packet)

    def press(self, key: str, modifiers: List[Modifier] = []) -> None:
        if key not in HID_MAPPING:
            raise InvalidKey(key)
        _, shift = HID_MAPPING[key]
        if shift:
            modifiers = modifiers.copy()
            modifiers.append("shift")
        self.send((key, "", "", "", "", ""), modifiers)

    def release(self) -> None:
        """释放按键"""
        self.send(("", "", "", "", "", ""))

    def press_and_release(
            self,
            key: str,
            modifiers: List[Modifier] = [],
            min_interval: float = 0.02,
            max_interval: float = 0.06,
    ) -> None:
        """
        按下单个按键 或者组合按键
        :param key: 需要按下的按键
        :param modifiers: 控制按键
        :param min_interval: 默认即可
        :param max_interval: 默认即可
        :return:
        """
        self.press(key, modifiers)
        time.sleep(random.uniform(min_interval, max_interval))
        self.release()

    def trigger_keys(
            self, keys: list[str], modifiers: List[Modifier] = []
    ) -> None:
        press_keys = keys.copy()
        press_modifiers = modifiers.copy()
        press_keys = list(set(press_keys))
        press_modifiers = list(set(press_modifiers))
        # Supports press to 6 normal buttons at the same time
        if len(press_keys) > 6:
            raise TooManyKeysError(
                "CH9329最多支持同时按下6个按键。"
            )
        if len(modifiers) > 8:
            raise TooManyKeysError(
                "CH9329最多支持同时按下8个控制键。"
            )
        # if len(keys) <= 6, add empty keys
        while len(press_keys) != 6:
            press_keys.append("")

        self.send(
            (
                press_keys[0],
                press_keys[1],
                press_keys[2],
                press_keys[3],
                press_keys[4],
                press_keys[5],
            ),
            press_modifiers,
        )

    def write(
            self,
            text: str,
            min_interval: float = 0.02,
            max_interval: float = 0.06,
    ) -> None:
        """
        按下多个按键,一般用于输入
        :param text: 按键文本
        :param min_interval: 默认即可
        :param max_interval: 默认即可
        :return:
        """
        for char in text:
            self.press_and_release(char, [], min_interval, max_interval)
            time.sleep(random.uniform(min_interval, max_interval))

    def longpress(self,key:str):
        """
        长按按键
        :param key: 按键
        :return:
        """
        self.press(key)


