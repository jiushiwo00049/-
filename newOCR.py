import pyautogui  # 导入pyautogui库，用于截屏
from paddleocr import PaddleOCR  # 导入PaddleOCR库，用于OCR识别
import edge_tts  # 导入edge_tts库，用于文本转语音
import asyncio  # 导入asyncio库，用于异步操作
import requests  # 导入requests库，用于HTTP请求
import time  # 导入time库，用于时间操作
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QSizeGrip  # 导入PyQt5库，用于GUI
from PyQt5.QtCore import Qt, QPoint  # 导入PyQt5核心库，用于GUI
import sys  # 导入sys库，用于系统操作
import keyboard  # 导入keyboard库，用于键盘操作
import threading  # 导入threading库，用于线程操作

# 新增导入
REGION = (0, 1186, 2500, 274)  # 定义截屏区域
VOICE = 'en-US-EmmaMultilingualNeural'  # 定义语音合成的声音
NIUTRANS_API_KEY = 'cee00dfa1aa4cd144da8cb9773bde738'  # 请替换为你的API KEY

# 截取指定区域的屏幕并保存为图片
def capture_region(region):  # 定义截屏函数
    img = pyautogui.screenshot(region=region)  # 截取屏幕指定区域
    img.save('temp_region.png')  # 保存截屏为图片
    return 'temp_region.png'  # 返回图片路径

# 对图片进行英文OCR识别，只保留英文字符
def ocr_english(img_path):  # 定义OCR识别函数
    ocr = PaddleOCR(use_angle_cls=True, lang='en')  # 初始化OCR对象
    result = ocr.ocr(img_path, cls=True)  # 进行OCR识别
    texts = []  # 初始化文本列表
    for line in result:  # 遍历识别结果
        for box in line:  # 遍历每个识别框
            text = box[1][0]  # 获取识别文本
            # 只保留英文字符
            if all(ord(c) < 128 for c in text) and text.strip():  # 判断是否为英文字符
                texts.append(text)  # 添加到文本列表
    return ' '.join(texts)  # 返回识别文本

# 使用edge_tts进行英文语音朗读
async def tts_read(text, voice=VOICE):  # 定义文本转语音函数
    communicate = edge_tts.Communicate(text, voice=voice)  # 初始化语音合成对象
    await communicate.save("output.mp3")  # 保存语音为MP3文件
    import pygame  # 导入pygame库，用于音频播放
    pygame.mixer.init()  # 初始化音频混音器
    pygame.mixer.music.load("output.mp3")  # 加载MP3文件
    pygame.mixer.music.play()  # 播放音频
    while pygame.mixer.music.get_busy():  # 检查音频是否播放完毕
        pygame.time.Clock().tick(10)  # 控制播放速度
    pygame.mixer.music.unload()  # 卸载音频文件

# 使用NiuTrans API将英文翻译为中文
def niutrans_translate(text, api_key):  # 定义翻译函数
    url = "https://api.niutrans.com/NiuTransServer/translation"  # 定义API URL
    data = {  # 定义请求数据
        "from": "en",  # 源语言
        "to": "zh",  # 目标语言
        "apikey": api_key,  # API密钥
        "src_text": text  # 源文本
    }
    resp = requests.post(url, data=data)  # 发送POST请求
    if resp.status_code == 200:  # 检查响应状态
        res = resp.json()  # 解析响应JSON
        return res.get("tgt_text", "翻译失败")  # 返回翻译结果
    else:
        return "翻译请求失败"  # 返回失败信息

# 翻译弹窗类，支持拖动、缩放、透明度和字体大小调节
class TranslationPopup(QWidget):  # 定义弹窗类
    def __init__(self):  # 初始化函数
        super().__init__()  # 调用父类初始化
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)  # 设置窗口标志
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.setFocusPolicy(Qt.NoFocus)  # 设置焦点策略
        self.dragging = False  # 初始化拖动状态
        self.drag_position = QPoint()  # 初始化拖动位置

        # 主布局
        main_layout = QVBoxLayout(self)  # 创建主布局
        main_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局边距
        main_layout.setSpacing(0)  # 设置布局间距

        # 顶部可拖动区域
        self.header = QLabel("翻译")  # 创建顶部标签
        self.header.setStyleSheet("QLabel { background-color: rgba(200,200,200,180); color: black; font-size: 16px; padding: 6px; border-top-left-radius: 10px; border-top-right-radius: 10px; }")  # 设置标签样式
        self.header.setFixedHeight(32)  # 设置标签高度
        main_layout.addWidget(self.header)  # 添加标签到布局

        # 内容标签
        self.label = QLabel("", self)  # 创建内容标签
        self.label.setStyleSheet("QLabel { background-color: rgba(255,255,255,180); color: black; font-size: 24px; padding: 20px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; }")  # 设置标签样式
        self.label.setWordWrap(True)  # 设置标签自动换行
        main_layout.addWidget(self.label, 1)  # 添加标签到布局

        # 底部布局（滑块+缩放）
        bottom_layout = QHBoxLayout()  # 创建底部布局
        bottom_layout.setContentsMargins(10, 0, 10, 10)  # 设置布局边距

        # 透明度滑块
        self.opacity_slider = QSlider(Qt.Horizontal)  # 创建透明度滑块
        self.opacity_slider.setMinimum(30)  # 设置滑块最小值
        self.opacity_slider.setMaximum(100)  # 设置滑块最大值
        self.opacity_slider.setValue(50)  # 设置滑块初始值
        self.opacity_slider.setFixedWidth(120)  # 设置滑块宽度
        self.opacity_slider.valueChanged.connect(self.on_opacity_change)  # 连接滑块变化信号
        bottom_layout.addWidget(self.opacity_slider)  # 添加滑块到布局

        # 增加间隔
        bottom_layout.addSpacing(20)  # 增加间隔

        # 文字大小滑块
        self.fontsize_slider = QSlider(Qt.Horizontal)  # 创建文字大小滑块
        self.fontsize_slider.setMinimum(12)  # 设置滑块最小值
        self.fontsize_slider.setMaximum(48)  # 设置滑块最大值
        self.fontsize_slider.setValue(24)  # 设置滑块初始值
        self.fontsize_slider.setFixedWidth(120)  # 设置滑块宽度
        self.fontsize_slider.valueChanged.connect(self.on_fontsize_change)  # 连接滑块变化信号
        bottom_layout.addWidget(self.fontsize_slider)  # 添加滑块到布局

        # 右下角缩放
        self.size_grip = QSizeGrip(self)  # 创建缩放控件
        bottom_layout.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)  # 添加缩放控件到布局

        main_layout.addLayout(bottom_layout)  # 添加底部布局到主布局

        self.resize(600, 200)  # 设置窗口大小
        # 初始位置设置为屏幕右上角
        screen = QApplication.primaryScreen()  # 获取主屏幕
        screen_geometry = screen.geometry()  # 获取屏幕几何信息
        x = screen_geometry.width() - self.width() - 20  # 距离右边20像素
        y = 20  # 距离顶部20像素
        self.move(x, y)  # 移动窗口到指定位置
        self.set_popup_opacity(0.5)  # 设置窗口透明度
        self.show()  # 显示窗口

    def update_text(self, text):  # 更新文本内容
        self.label.setText(text)  # 设置标签文本

    def set_popup_opacity(self, opacity):  # 设置窗口透明度
        self.setWindowOpacity(opacity)  # 设置窗口透明度

    def on_opacity_change(self, value):  # 透明度滑块变化处理
        self.set_popup_opacity(value / 100.0)  # 更新窗口透明度

    def on_fontsize_change(self, value):  # 字体大小滑块变化处理
        # 只调整内容字体大小
        self.label.setStyleSheet(f"QLabel {{ background-color: rgba(255,255,255,180); color: black; font-size: {value}px; padding: 20px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; }}")  # 更新标签样式

    # 鼠标拖动弹窗
    def mousePressEvent(self, event):  # 鼠标按下事件处理
        if event.button() == Qt.LeftButton and self.header.geometry().contains(event.pos()):  # 判断是否在可拖动区域
            self.dragging = True  # 设置拖动状态
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()  # 记录拖动位置
            event.accept()  # 接受事件

    def mouseMoveEvent(self, event):  # 鼠标移动事件处理
        if self.dragging:  # 判断是否正在拖动
            self.move(event.globalPos() - self.drag_position)  # 移动窗口
            event.accept()  # 接受事件

    def mouseReleaseEvent(self, event):  # 鼠标释放事件处理
        self.dragging = False  # 取消拖动状态

# 实时OCR主循环，定时识别、翻译并朗读新英文内容
def realtime_ocr_loop(region, popup):  # 定义实时OCR循环函数
    last_text = ""  # 初始化上次识别文本
    ocr = PaddleOCR(use_angle_cls=True, lang='en')  # 初始化OCR对象
    while True:  # 循环执行
        try:
            img = pyautogui.screenshot(region=region)  # 截取屏幕指定区域
            img.save('temp_region.png')  # 保存截屏为图片
            english_text = ocr_english('temp_region.png')  # 进行OCR识别
            if english_text and english_text != last_text:  # 判断是否有新识别文本
                print("识别到英文：", english_text)  # 打印识别文本
                chinese = niutrans_translate(english_text, NIUTRANS_API_KEY)  # 翻译文本
                print("翻译为中文：", chinese)  # 打印翻译结果
                popup.update_text(chinese)  # 更新弹窗文本
                QApplication.processEvents()  # 处理挂起的事件
                # 朗读放到新线程，避免阻塞界面
                threading.Thread(target=lambda: asyncio.run(tts_read(english_text)), daemon=True).start()  # 启动新线程进行朗读
                last_text = english_text  # 更新上次识别文本
            QApplication.processEvents()  # 处理挂起的事件
            time.sleep(8)  # 暂停5秒
        except Exception as e:  # 异常处理
            print(f"Error: {str(e)}")  # 打印错误信息
            time.sleep(3)  # 暂停10秒

if __name__ == "__main__":  # 主程序入口
    print("实时OCR已启动，按Ctrl+C退出。")  # 打印启动信息
    app = QApplication(sys.argv)  # 创建应用程序对象
    popup = TranslationPopup()  # 创建弹窗对象
    try:
        threading.Thread(target=realtime_ocr_loop, args=(REGION, popup), daemon=True).start()  # 启动实时OCR循环线程
        sys.exit(app.exec_())  # 运行应用程序事件循环
    except KeyboardInterrupt:  # 键盘中断处理
        print("已退出。")  # 打印退出信息