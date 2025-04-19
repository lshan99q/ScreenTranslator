import pytesseract
import pyautogui
from PIL import Image, ImageFilter, ImageTk, ImageDraw, ImageFont
import logging
from datetime import datetime
import os
import mss
import time
import tkinter as tk
from tkinter import messagebox, simpledialog

class ScreenTranslator:
    def __init__(self):
        # 初始化日志系统
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            filename='logs/translator.log',
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logging.info('Screen Translator initialized')
        
        self.root = tk.Tk()
        self.root.title("屏幕翻译器")
        self.root.geometry("300x150")

        # 检查API密钥配置
        self.check_api_key()
        
        self.start_btn = tk.Button(
            self.root, 
            text="选择翻译区域", 
            command=self.select_region
        )
        self.start_btn.pack(pady=20)
        
        self.status = tk.Label(self.root, text="准备就绪")
        self.status.pack()
        
        self.region = None
        self.running = False

    def select_region(self):
        self.status.config(text="请用鼠标拖选翻译区域")
        self.root.withdraw()
        time.sleep(0.5)
        
        try:
            # 颜色配置常量
            SELECTION_COLOR = "lightblue"
            BORDER_COLOR = "blue"
            
            # 创建全屏透明选择窗口
            selection_window = tk.Toplevel()
            selection_window.attributes("-fullscreen", True)
            selection_window.attributes("-alpha", 0.4)  # 优化后的透明度
            selection_window.attributes("-topmost", True)
            selection_window.overrideredirect(True)  # 移除窗口边框
            
            # 创建带透明度的画布
            canvas = tk.Canvas(selection_window, bg=SELECTION_COLOR, highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # 初始全屏透明覆盖
            screen_width = selection_window.winfo_screenwidth()
            screen_height = selection_window.winfo_screenheight()
            canvas.create_rectangle(0, 0, screen_width, screen_height, 
                                 fill=SELECTION_COLOR, outline=BORDER_COLOR, width=0)
            
            # 鼠标拖动选择区域
            start_x, start_y = 0, 0
            rect = None
            
            def on_press(event):
                nonlocal start_x, start_y, rect
                start_x, start_y = event.x, event.y
                rect = canvas.create_rectangle(
                    start_x, start_y, start_x, start_y,
                    outline=BORDER_COLOR, width=2, fill=SELECTION_COLOR
                )
            
            def on_drag(event):
                nonlocal rect
                if rect:
                    canvas.coords(rect, start_x, start_y, event.x, event.y)
                    # 更新半透明填充区域
                    canvas.itemconfig(rect, fill=SELECTION_COLOR)
            
            def on_release(event):
                nonlocal rect
                x1, y1 = start_x, start_y
                x2, y2 = event.x, event.y
                self.region = (min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
                selection_window.destroy()
                self.status.config(text=f"已选择区域: {self.region}")
                self.start_translation()
            
            canvas.bind("<ButtonPress-1>", on_press)
            canvas.bind("<B1-Motion>", on_drag)
            canvas.bind("<ButtonRelease-1>", on_release)
        except Exception as e:
            messagebox.showerror("错误", f"区域选择失败: {str(e)}")
            self.root.deiconify()

    def start_translation(self):
        self.running = True
        self.start_btn.config(text="停止翻译", command=self.stop_translation)
        self.translate_loop()

    def stop_translation(self):
        self.running = False
        self.start_btn.config(text="选择翻译区域", command=self.select_region)
        self.status.config(text="翻译已停止")

    def translate_loop(self):
        while self.running:
            try:
                with mss.mss() as sct:
                    monitor = {
                        "top": self.region[1], 
                        "left": self.region[0],
                        "width": self.region[2],
                        "height": self.region[3]
                    }
                    img = sct.grab(monitor)
                    text = pytesseract.image_to_string(Image.frombytes("RGB", img.size, img.rgb))
                    if text.strip():
                        import requests
                        headers = {
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        }
                        data = {
                            "model": "deepseek-chat",
                            "messages": [{
                                "role": "user",
                                "content": f"Translate this English text to Simplified Chinese: {text}"
                            }]
                        }
                        response = requests.post(
                            "https://api.deepseek.com/v1/chat/completions",
                            headers=headers,
                            json=data
                        )
                        translated = response.json()["choices"][0]["message"]["content"]
                        print(f"原文: {text}\n译文: {translated}")
                        
                        # 创建/更新覆盖窗口显示翻译结果
                        try:
                            if hasattr(self, 'overlay') and self.overlay.winfo_exists():
                                self.overlay.destroy()
                            
                            self.overlay = tk.Toplevel()
                            self.overlay.overrideredirect(True)
                            self.overlay.attributes("-topmost", True)
                            self.overlay.attributes("-alpha", 0.7)  # 70%不透明度
                            
                            # 创建半透明覆盖层
                            with mss.mss() as sct:
                                monitor = {
                                    "top": self.region[1],
                                    "left": self.region[0],
                                    "width": self.region[2],
                                    "height": self.region[3]
                                }
                                img = sct.grab(monitor)
                                # 确保图像为RGBA模式
                                img = Image.frombytes("RGB", img.size, img.rgb).convert('RGBA')
                                
                                # 创建纯色半透明覆盖层
                                overlay_img = Image.new('RGBA', img.size, (0,0,0,180))
                                
                                # 精确合成覆盖层
                                img = Image.alpha_composite(img, overlay_img)
                                
                                # 创建新的透明背景图像用于文本显示
                                text_bg = Image.new('RGBA', img.size, (0,0,0,0))
                                draw = ImageDraw.Draw(text_bg)
                                
                                # 计算文本位置和大小 (兼容Pillow 9.0+)
                                bbox = draw.textbbox((0,0), translated, font=ImageFont.load_default())
                                text_width = bbox[2] - bbox[0]
                                text_height = bbox[3] - bbox[1]
                                x = (img.size[0] - text_width) // 2
                                y = (img.size[1] - text_height) // 2
                                
                                # 绘制文本
                                draw.text((x, y), translated, fill=(255,255,255,255))
                                
                                # 合并所有图层
                                img = Image.alpha_composite(img, text_bg)
                                
                                # 转换为Tkinter兼容格式
                                photo = ImageTk.PhotoImage(img)
                            
                            # 设置覆盖窗口
                            self.overlay.geometry(f"{self.region[2]}x{self.region[3]}+{self.region[0]}+{self.region[1]}")
                            label = tk.Label(self.overlay, image=photo, text=translated,
                                           compound="center", fg="white",
                                           font=("Microsoft YaHei", 12))
                            label.image = photo
                            label.pack()
                            
                            # 添加关闭按钮
                            close_btn = tk.Button(self.overlay, text="×", command=self.overlay.destroy,
                                                  bg="red", fg="white", bd=0)
                            close_btn.place(x=self.region[2]-20, y=0, width=20, height=20)
                        except Exception as e:
                            error_msg = f"显示翻译出错: {str(e)}"
                            logging.error(error_msg)
                            print(error_msg)
                    self.root.update()
                time.sleep(1)
            except Exception as e:
                error_msg = f"翻译出错: {str(e)}"
                logging.error(error_msg)
                messagebox.showerror("错误", error_msg)
                self.stop_translation()

    def check_api_key(self):
        try:
            import configparser
            config = configparser.ConfigParser()
            
            # 确保配置文件存在(使用UTF-8编码)
            if not os.path.exists('config.ini'):
                with open('config.ini', 'w', encoding='utf-8') as f:
                    config.add_section('Translation')
                    config.write(f)
            
            config.read('config.ini', encoding='utf-8')
            
            if not config.has_section('Translation'):
                config.add_section('Translation')
                
            if 'api_key' not in config['Translation'] or not config['Translation']['api_key']:
                # 弹出对话框让用户输入API密钥
                self.root.withdraw()
                api_key = tk.simpledialog.askstring(
                    "API密钥配置",
                    "请输入DeepSeek API密钥:",
                    parent=self.root
                )
                if api_key:
                    config['Translation']['api_key'] = api_key
                    with open('config.ini', 'w', encoding='utf-8') as f:
                        config.write(f)
                else:
                    messagebox.showerror("错误", "必须提供API密钥才能使用翻译功能")
                    self.root.destroy()
                    os._exit(1)  # 直接退出程序
                    return
                    
            self.api_key = config['Translation']['api_key']
            self.root.deiconify()
        except Exception as e:
            messagebox.showerror("初始化错误", f"配置读取失败: {str(e)}")
            logging.error(f"配置读取失败: {str(e)}")
            self.root.destroy()
            os._exit(1)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenTranslator()
    app.run()
