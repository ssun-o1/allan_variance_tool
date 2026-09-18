@echo off
chcp 65001 >nul

:: 项目信息汇总脚本

echo ==========================================
echo 艾伦方差分析工具 - 项目信息
echo ==========================================
echo.
echo 📁 项目位置: %cd%
echo 📅 创建时间: %date% %time%
echo.
echo 📋 文件列表:
echo ----------------------------------------
dir /B
echo.
echo ==========================================
echo 🚀 快速开始
echo ==========================================
echo.
echo 【开发测试】
echo   1. 安装依赖:
echo      python -m venv venv
echo      venv\Scripts\activate
echo      pip install -r requirements.txt
echo.
echo   2. 运行程序:
echo      python allan_variance_gui.py
echo.
echo 【打包 Windows 应用】
echo   方式一（安装程序）:
echo     build_windows_complete.bat
echo     生成: dist\艾伦方差分析工具_v1.0.0_Setup.exe
echo.
echo   方式二（便携版）:
echo     build_windows_portable.bat
echo     生成: dist\艾伦方差分析工具_v1.0.0_便携版.zip
echo.
echo ==========================================
echo 📖 文档说明
echo ==========================================
echo   README.md      - 完整项目文档
echo   QUICKSTART.md  - 快速开始指南
echo.
echo ==========================================
echo ✅ 项目已成功创建到桌面！
echo ==========================================
echo.
pause
