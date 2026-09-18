#!/bin/bash

set -e  # 遇到错误立即退出

APP_NAME="艾伦方差分析工具"

echo "=========================================="
echo "macOS 完整打包流程"
echo "=========================================="

# Step 1: 创建虚拟环境
echo ""
echo "[1/5] 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Step 2: 安装依赖
echo ""
echo "[2/5] 安装依赖..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q

# Step 3: 打包应用
echo ""
echo "[3/5] 打包应用..."
pyinstaller build_spec.py --clean --noconfirm

# 检查 .app 是否生成成功
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "❌ 应用打包失败"
    exit 1
fi

echo "✅ 应用打包成功"

# Step 4: 创建 DMG
echo ""
echo "[4/5] 创建 DMG 安装包..."
chmod +x create_dmg.sh
./create_dmg.sh

# Step 5: 清理
echo ""
echo "[5/5] 清理构建文件..."
rm -rf build
rm -rf __pycache__
deactivate

echo ""
echo "=========================================="
echo "✅ 全部完成！"
echo "=========================================="
echo ""
echo "生成的文件："
echo "  - 应用程序: dist/${APP_NAME}.app"
echo "  - DMG 安装包: dist/${APP_NAME}_v1.0.0.dmg"
echo ""
echo "分发建议："
echo "  - 分发 DMG 文件给用户"
echo "  - 用户双击 DMG，拖动应用到 Applications 即可"
echo ""
echo "测试运行："
echo "  open dist/${APP_NAME}.app"
