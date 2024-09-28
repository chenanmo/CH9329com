# 代码抄的改的他的

[sandbox-pokhara/ch9329](https://pages.github.com/)

## 注册键盘鼠标
将下载解压后的文件夹重命名为ch9329
```python

from ch9329 import CH9329

ch9329 = CH9329("COM3", 115200, timeout=1, screenx=1920, screeny=1080)
"""
串口
波特率
超时时间
屏幕X
屏幕Y
"""

#  释放串口
ch9329.close()
```

### 操作键盘

```python
from ch9329 import CH9329

ch9329 = CH9329("COM3", 115200, timeout=1, screenx=1920, screeny=1080)

# 自定义发送按键, 最多支持6个按键,modifiers为控制键,可选
ch9329.keyboard.send(("ctrl", "alt", "del", "", "", ""), modifiers=[])
ch9329.keyboard.send(("alt", "del", "", "", "", ""), modifiers=["ctrl"])

# 按下单个按键, modifiers为控制键,可选,不释放则为长按
ch9329.keyboard.press("a", modifiers=["shift"])

# 释放所有按键
ch9329.keyboard.release()

# 按下后自动释放按键, min_interval和max_interval为释放延迟, 默认0.02秒到0.06秒
ch9329.keyboard.press_and_release("a", modifiers="shift", min_interval=0.02, max_interval=0.06)

# 和send一样,多了个校验,确保不超出6个
ch9329.keyboard.trigger_keys(["ctrl", "alt", "del", "", "", ""], modifiers=[])
ch9329.keyboard.trigger_keys(["alt", "del", "", "", "", ""], modifiers=["ctrl"])

# 多字符输入,适合输入多个按键
ch9329.keyboard.write("Hello World\n")
ch9329.keyboard.write("abcdefghijklmnopqrstuvwxyz\n")
ch9329.keyboard.write("ABCDEFGHIJKLMNOPQRSTUVWXYZ\n")
ch9329.keyboard.write("0123456789\n")
ch9329.keyboard.write("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~\n")

# press的简单使用, 按下某个按键,长按不释放
ch9329.keyboard.longpress("e")
```

### 操作鼠标

```python
from ch9329 import CH9329

ch9329 = CH9329("COM3", 115200, timeout=1, screenx=1920, screeny=1080)

# 绝对移动
ch9329.mouse.absolute_move(1458, 544)

# 相对移动,最大移动127个像素
ch9329.mouse.relative_move(127, -127)

# 按下左键,会自动释放, 支持"left", "right", "center"
ch9329.mouse.click("left")

# 长按左键,不会释放, 支持"left", "right", "center"
ch9329.mouse.press("left")

# 释放鼠标按键
ch9329.mouse.release()

# 滚动鼠标轮子,最大轮动127
ch9329.mouse.wheel(-127)
```


