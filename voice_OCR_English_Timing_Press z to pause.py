# 导入 time 模块，用于处理时间相关操作，如计时、休眠等
import time
# 导入 numpy 模块，用于处理多维数组和矩阵运算，这里主要用于图像数据处理
import numpy as np
# 导入 pyautogui 模块，用于自动化操作，如屏幕截图
import pyautogui
# 导入 pyperclip 模块，用于操作剪贴板，实现文本的复制和粘贴
import pyperclip
# 从 paddleocr 库中导入 PaddleOCR 类，用于进行光学字符识别（OCR）
from paddleocr import PaddleOCR
# 从 pynput 库中导入 keyboard 模块，用于监听键盘事件
from pynput import keyboard
# 导入 edge-tts 库，用于实现文本转语音功能
import edge_tts
# 导入 os 模块，用于与操作系统进行交互，如文件操作
import os
# 导入 asyncio 库，用于实现异步编程，提高程序的并发性能
import asyncio
# 导入 pygame 库，用于播放音频文件
import pygame
# 导入 configparser 库，用于读取和写入配置文件
import configparser

# 初始化 pygame 的音频模块，为后续播放音频做准备
pygame.mixer.init()

# 定义发音人列表，键为编号，值为 edge-tts 支持的发音人名称
voices = {
    # 中文发音人：晓晓
    1: 'zh-CN-XiaoxiaoNeural',
    # 中文发音人：晓伊
    2: 'zh-CN-XiaoyiNeural',
    # 中文发音人：云健
    3: 'zh-CN-YunjianNeural',
    # 中文发音人：云希
    4: 'zh-CN-YunxiNeural',
    # 中文发音人：云霞
    5: 'zh-CN-YunxiaNeural',
    # 中文发音人：云扬
    6: 'zh-CN-YunyangNeural',
    # 中文发音人：抚宁
    7: 'zh-CN-FuningNeural',
    # 英文发音人：Ava
    8: 'en-US-AvaMultilingual',#xxx
    9: 'en-US-AriaNeural',
    10: 'en-US-DavisNeural',
    11: 'en-US-GuyNeural',
    12: 'en-US-JaneNeural',
    13: 'en-US-MichelleNeural',
    14: 'en-GB-LibbyNeural',
    15: 'en-GB-MaisieNeural',#girl
    16: 'en-GB-RyanNeural',
    17: 'en-AU-NatashaNeural',
    18: 'en-AU-WilliamNeural',
    19: 'en-CA-ClaraNeural',#g
    20: 'en-CA-LiamNeural',
    21: 'en-US-EmmaMultilingualNeural',#good
    22: 'en-US-AvaMultilingualNeural',#goo
    23: 'af-ZA-AdriNeural',
    24: 'en-AU-NatashaNeural',
    25: 'en-AU-WilliamNeural',
    26: 'en-GB-MaisieNeural',#go
    27: 'en-GB-SoniaNeural',#goo
    28: 'en-IE-EmilyNeural',#good
    29: 'en-SG-LunaNeural'#goo
}

# 创建一个 ConfigParser 对象，用于读取和写入配置文件
config = configparser.ConfigParser()

# 检查配置文件 jtb.ini 是否存在
if os.path.exists("jtb.ini"):
    # 如果存在，则读取配置文件
    config.read("jtb.ini")
    # 获取配置文件中 SETTINGS 部分的配置信息
    saved_settings = config["SETTINGS"]
    # 从配置文件中获取语速设置，默认为 1.0
    rate_input = saved_settings.get("rate", "1.0").strip()
    # 从配置文件中获取发音人编号，默认为 1
    voice_choice = int(saved_settings.get("voice_choice", "1"))
    # 从配置文件中获取是否启用快捷键监控功能的设置，默认为不启用
    use_hotkey = saved_settings.get("use_hotkey", "n") == 'y'
    # 从配置文件中获取快捷键设置，默认为空
    hotkey = saved_settings.get("hotkey", "")
    # 从配置文件中获取是否只转换英文内容的设置，默认为否
    convert_english_only = saved_settings.get("convert_english_only", "n") == 'y'
else:
    # 如果配置文件不存在，则提示用户输入语速
    rate_input = input("请输入语速（例如 '1.0' 表示正常速度，'1.5' 表示1.5倍速度，默认是 '1.0'）: ").strip()
    try:
        # 将用户输入的语速转换为浮点数
        rate = float(rate_input)
        # 计算语速百分比，用于 edge-tts 的语速设置
        rate_percent = f"+{int((rate - 1) * 100)}%"
    except ValueError:
        # 如果用户输入无效，则使用默认语速
        rate_percent = "+0%"

    # 打印发音人选项，供用户选择
    print("请选择发音人：")
    for key, value in voices.items():
        print(f"{key}: {value}")

    # 提示用户输入发音人编号
    voice_choice = int(input("请输入发音人编号: "))
    # 根据用户输入的编号选择发音人，默认使用晓晓
    selected_voice = voices.get(voice_choice, 'zh-CN-XiaoxiaoNeural')

    # 提示用户是否启用快捷键监控功能
    use_hotkey = input("是否启用快捷键监控功能？(y/n): ").strip().lower() == 'y'

    # 如果启用快捷键监控功能，则提示用户按下快捷键组合
    if use_hotkey:
        print("请按下要监控的快捷键组合...")
        hotkey = keyboard.read_hotkey()
        print(f"您选择的快捷键组合是: {hotkey}")
    else:
        hotkey = ""

    # 提示用户是否只转换英文内容
    convert_english_only = input("是否只转换英文内容？(y/n): ").strip().lower() == 'y'

    # 将用户的设置保存到配置文件的 SETTINGS 部分
    config["SETTINGS"] = {
        "rate": rate_input,
        "voice_choice": voice_choice,
        "use_hotkey": 'y' if use_hotkey else 'n',
        "hotkey": hotkey,
        "convert_english_only": 'y' if convert_english_only else 'n'
    }

    # 将配置信息写入 jtb.ini 文件
    with open("jtb.ini", "w") as configfile:
        config.write(configfile)

# 用户配置已读取或设置，现在初始化其他变量
try:
    # 使用读取到或输入的 rate_input 进行语速设置
    rate = float(rate_input)
    rate_percent = f"+{int((rate - 1) * 100)}%"
except ValueError:
    # 如果转换失败，则使用默认语速
    rate_percent = "+0%"

# 根据用户选择的编号选择发音人，默认使用晓晓
selected_voice = voices.get(voice_choice, 'zh-CN-XiaoxiaoNeural')

# 初始化变量，用于存储上一次剪贴板的内容
previous_clipboard_content = ""

# 定义异步函数，用于将文本转换为语音并保存为音频文件
async def text_to_speech(text, output_file="output.mp3"):
    # 创建 edge-tts 的 Communicate 对象，将发音人设定为用户选择的发音人，并设置语速
    communicator = edge_tts.Communicate(text, voice=selected_voice, rate=rate_percent)
    # 调用 save 方法将语音保存为音频文件
    await communicator.save(output_file)

# 定义函数，用于播放音频文件并记录生成时间
def play_audio_file(file_path, start_time):
    # 使用 pygame 加载音频文件
    pygame.mixer.music.load(file_path)

    # 记录结束时间
    end_time = time.time()
    # 计算生成时间
    elapsed_time = end_time - start_time
    print(f"生成时间: {elapsed_time:.2f} 秒")

    # 播放音频文件
    pygame.mixer.music.play()

    # 循环检查音频是否播放完毕
    while pygame.mixer.music.get_busy():
        # 控制循环频率，每 100 毫秒检查一次
        pygame.time.Clock().tick(10)

    # 等待播放完毕后卸载音频文件
    pygame.mixer.music.unload()

# 定义函数，用于安全删除文件，处理可能的权限错误
def safe_remove(file_path, retries=3, delay=1):
    """
    安全删除文件的方法
    :param file_path: 要删除的文件路径
    :param retries: 最大重试次数
    :param delay: 每次重试之间的延迟（秒）
    """
    for i in range(retries):
        try:
            # 尝试删除文件
            os.remove(file_path)
            print(f"播放完成")
            break
        except PermissionError as e:
            # 如果删除失败，打印错误信息并重试
            print(f"删除文件失败，重试 {i+1}/{retries}...")
            time.sleep(delay)
        except Exception as e:
            # 处理其他异常
            print(f"发生意外错误: {e}")
            break

# 定义函数，用于检查文本是否只包含英文字符和常用标点符号
def is_english(text):
    try:
        # 遍历文本中的每个字符，检查其 Unicode 编码是否小于 128
        return all(ord(c) < 128 for c in text)
    except:
        # 处理异常情况，返回 False
        return False

# 定义函数，用于检查文本是否为有效的字符串且长度大于 0
def is_valid_text(text):
    try:
        # 检查文本是否为字符串类型且去除首尾空格后长度大于 0
        return isinstance(text, str) and len(text.strip()) > 0
    except:
        # 处理异常情况，返回 False
        return False

# 定义函数，用于处理剪贴板中的文本，包括语音合成和播放
def process_clipboard_text(text):
    global previous_clipboard_content
    try:
        # 仅在剪贴板内容是有效文本且与上次不同的时候处理
        if is_valid_text(text) and text != previous_clipboard_content:
            # 更新上一次剪贴板的内容
            previous_clipboard_content = text

            # 根据用户设置只处理英文内容
            if not convert_english_only or is_english(text):
                # 记录开始时间
                start_time = time.time()
                print(f"新文本: {text}")
                # 使用 edge-tts 合成语音并播放
                output_file = "output.mp3"
                # 异步运行 text_to_speech 函数
                asyncio.run(text_to_speech(text, output_file))

                # 检查音频文件是否成功生成且有效
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    play_audio_file(output_file, start_time)

                # 播放完毕后删除音频文件
                safe_remove(output_file)
    except pyperclip.PyperclipException as e:
        # 处理剪贴板操作异常
        print(f"读取剪贴板内容时出现错误: {e}")

# 定义全局变量，用于控制程序的暂停状态
paused = False

# 定义键盘按下事件处理函数，用于切换程序的暂停状态
def on_press(key):
    global paused
    try:
        # 当按下 'z' 键时，切换暂停状态
        if key.char.lower() == 'z':
            paused = not paused
            status = "PAUSED" if paused else "RESUMED"
            print(f"[{status}] Press Z to toggle")
    except AttributeError:
        # 处理非字符键的情况
        pass

# 启动键盘监听，将 on_press 函数作为回调函数
listener = keyboard.Listener(on_press=on_press)
# 将监听器设置为守护线程
listener.daemon = True
# 启动监听器
listener.start()

# 初始化 PaddleOCR 对象，支持英文识别，不使用 GPU
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

# 定义函数，用于监控指定区域的屏幕截图并进行 OCR 识别
def monitor_region(region):
    global paused
    # 初始化变量，用于存储上一次识别的文本
    last_text = ''
    while True:
        try:
            # 如果程序处于暂停状态，则休眠 0.5 秒后继续循环
            if paused:
                time.sleep(0.5)
                continue

            # 对指定区域进行屏幕截图
            screenshot = pyautogui.screenshot(region=region)
            # 将截图转换为 RGB 格式的 NumPy 数组
            img_array = np.array(screenshot.convert('RGB'))

            # 使用 PaddleOCR 对图像进行识别
            result = ocr.ocr(img_array)

            # 提取识别结果中的文本行
            text_lines = [line[1][0] for line in result[0]] if result else []
            # 将文本行合并为一个字符串，并去除首尾空格，去掉换行符
            text = ''.join(text_lines).strip()

            # 如果识别到的文本不为空且与上次不同，则将其复制到剪贴板并处理
            if text and text != last_text:
                pyperclip.copy(text)
                print('Copied to clipboard:', text)
                last_text = text
                # 调用语音合成和播放功能
                process_clipboard_text(text)

            # 休眠 8 秒后继续循环，根据阅读速度自行调整
            time.sleep(8)
        except Exception as e:
            # 处理异常情况，打印错误信息并休眠 2 秒
            print(f"Error: {str(e)}")
            time.sleep(2)

if __name__ == '__main__':
    # 程序启动前休眠 1 秒,防止误识别
    time.sleep(1)
    # 定义监控区域 (left, top, width, height)
    # 请根据实际需求修改这些值
    region = (0, 1186, 2500, 1460-1186)
    # 调用 monitor_region 函数开始监控
    monitor_region(region)