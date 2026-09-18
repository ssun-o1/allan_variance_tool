@echo off
chcp 65001 >nul
echo ==========================================
echo Windows 便携版打包
echo ==========================================

:: Step 1: 创建虚拟环境
echo.
echo [1/5] 创建虚拟环境...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

:: Step 2: 安装依赖
echo.
echo [2/5] 安装依赖...
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q

:: Step 3: 打包应用
echo.
echo [3/5] 打包应用...
pyinstaller build_spec.py --clean --noconfirm

if not exist "dist\艾伦方差分析工具.exe" (
    echo ❌ 应用打包失败
    pause
    exit /b 1
)

echo ✅ 应用打包成功

:: Step 4: 创建便携版目录
echo.
echo [4/5] 创建便携版目录...
set PORTABLE_DIR=艾伦方差分析工具_v1.0.0_便携版
if exist "%PORTABLE_DIR%" rmdir /s /q "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%"

:: 复制文件
copy "dist\艾伦方差分析工具.exe" "%PORTABLE_DIR%\"

:: 创建使用说明
(
echo 艾伦方差分析工具 v1.0.0 - 便携版
echo.
echo 【使用方法】
echo 1. 双击"艾伦方差分析工具.exe"启动程序
echo 2. 选择 CO2 和/或 CH4 数据文件
echo 3. 点击"开始分析"
echo 4. 结果自动保存到桌面
echo.
echo 【数据格式】
echo 制表符分隔的文本文件：
echo 时间戳    浓度值
echo 2024-01-01 10:00:00    415.23
echo.
echo 【注意事项】
echo - 首次运行可能被 Windows Defender 拦截，点击"更多信息"-"仍要运行"
echo - 无需安装，可直接运行
echo - 可放在 U 盘中随身携带
echo.
echo 【技术支持】
echo 如有问题请联系技术支持
) > "%PORTABLE_DIR%\使用说明.txt"

:: Step 5: 压缩
echo.
echo [5/5] 压缩为 ZIP 文件...
powershell Compress-Archive -Path "%PORTABLE_DIR%" -DestinationPath "dist\%PORTABLE_DIR%.zip" -Force

if exist "dist\%PORTABLE_DIR%.zip" (
    echo ✅ 便携版创建成功
    rmdir /s /q "%PORTABLE_DIR%"
) else (
    echo ❌ 压缩失败
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
echo   - 便携版压缩包: dist\%PORTABLE_DIR%.zip
echo.
echo 分发建议：
echo   - 直接分发 ZIP 文件
echo   - 用户解压后即可运行
echo.
pause
