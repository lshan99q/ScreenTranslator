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

## API密钥配置
1. 首次运行程序时会弹出对话框要求输入DeepSeek API密钥
2. 密钥将安全保存在config.ini文件中
3. 如需更改API密钥，可直接编辑config.ini文件或删除该文件后重新运行程序

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
- 请勿分享config.ini文件中的API密钥

## 依赖项
- pytesseract
- pyautogui  
- pillow
- mss
- requests
