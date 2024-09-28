from serial import Serial
from .keyboard import Keyboard
from .mouse import Mouse


class CH9329:
    ser: Serial = None

    def __init__(self, port: str, baudrate: int, timeout: int = 1, screenx: int = 1920, screeny: int = 1080):
        """
        CH9329控制的集合
        :param port: COM端口
        :param baudrate: 波特率
        :param timeout: 超时时间
        :param screenx: 屏幕X轴
        :param screeny: 屏幕Y轴
        """
        self.ser = Serial(port, baudrate, timeout=timeout)
        self.keyboard = Keyboard(self.ser)
        self.mouse = Mouse(self.ser, screenx, screeny)

    def close(self):
        """释放串口"""
        self.ser.close()
