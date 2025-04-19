@echo off
chcp 65001 >nul
echo 正在检查Python和pip安装...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未安装或未添加到系统PATH
    echo 请从 https://www.python.org/downloads/ 安装Python
    exit /b 1
)

pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: pip未安装
    echo 请确保Python安装时勾选了"Add Python to PATH"选项
    exit /b 1
)

echo 正在安装Python依赖...
pip install pytesseract pillow pyautogui mss
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    exit /b 1
)

echo 正在检查Tesseract OCR安装...
where tesseract >nul 2>&1
if %errorlevel% neq 0 (
    echo Tesseract OCR未安装，尝试自动安装...
    if exist "OCR\tesseract-ocr-w64-setup-5.5.0.20241111.exe" (
        echo 正在安装Tesseract OCR...
        start /wait "OCR\tesseract-ocr-w64-setup-5.5.0.20241111.exe" /S
        echo Tesseract OCR安装完成
    ) else (
        echo 错误: 未找到Tesseract OCR安装程序
        echo 请从 https://github.com/UB-Mannheim/tesseract/wiki 下载安装
        echo 并将安装包放置在OCR目录下
        exit /b 1
    )
) else (
    echo Tesseract OCR已正确安装
)

echo.
echo ========================================
echo 所有依赖项已成功安装！
echo 现在可以运行ScreenTranslator程序了
echo ========================================
exit /b 0
