@echo off
chcp 65001 >nul
echo ==========================================
echo Windows 完整打包流程
echo ==========================================

:: Step 1: 创建虚拟环境
echo.
echo [1/4] 创建虚拟环境...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

:: Step 2: 安装依赖
echo.
echo [2/4] 安装依赖...
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q

:: Step 3: 打包应用
echo.
echo [3/4] 打包应用...
pyinstaller build_spec.py --clean --noconfirm

if not exist "dist\艾伦方差分析工具.exe" (
    echo ❌ 应用打包失败
    pause
    exit /b 1
)

echo ✅ 应用打包成功

:: Step 4: 创建安装程序（需要安装 Inno Setup）
echo.
echo [4/4] 创建安装程序...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    echo ✅ 安装程序创建成功
) else (
    echo ⚠️  未检测到 Inno Setup，跳过安装程序创建
    echo 如需创建安装程序，请从以下网址下载 Inno Setup:
    echo https://jrsoftware.org/isdl.php
)

:: 清理
echo.
echo 清理构建文件...
rmdir /s /q build 2>nul
rmdir /s /q __pycache__ 2>nul
call deactivate

echo.
echo ==========================================
echo ✅ 全部完成！
echo ==========================================
echo.
echo 生成的文件：
echo   - 应用程序: dist\艾伦方差分析工具.exe
if exist "dist\艾伦方差分析工具_v1.0.0_Setup.exe" (
    echo   - 安装程序: dist\艾伦方差分析工具_v1.0.0_Setup.exe
)
echo.
echo 分发建议：
echo   - 有安装程序：分发 Setup.exe
echo   - 无安装程序：打包 .exe 为 .zip 分发
echo.
echo 测试运行：
echo   dist\艾伦方差分析工具.exe
echo.
pause
