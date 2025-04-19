# 屏幕实时翻译工具

## 功能概述
- 实时捕捉屏幕指定区域的英文内容
- 通过DeepSeek AI API翻译为简体中文
- 在原始内容上方叠加显示翻译结果
- 每秒自动刷新翻译内容

## 系统要求
- Windows 10/11
- Python 3.8+
- Tesseract OCR 5.0+

## 安装说明
1. 运行安装脚本:
   ```bash
   install_tesseract.bat
   ```
2. 安装完成后重启终端使环境变量生效

## 配置说明
编辑`config.ini`文件:
```ini
[Translation]
api_key = 您的DeepSeek API密钥
source_lang = 源语言代码(默认eng)
target_lang = 目标语言代码(默认chi_sim)

[Display]
refresh_rate = 刷新频率(秒)
```

## 使用说明
1. 运行主程序:
   ```bash
   python main.py
   ```
2. 点击"选择翻译区域"按钮
3. 用鼠标拖选需要翻译的屏幕区域
4. 翻译结果将实时显示在选定区域上方
5. 点击"停止翻译"结束程序

## 注意事项
- 确保网络连接正常以使用API
- 首次使用需安装Tesseract OCR
- 翻译质量取决于屏幕文字清晰度

## 依赖项
- pytesseract
- pyautogui  
- pillow
- mss
- requests
