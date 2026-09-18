#!/bin/bash

APP_NAME="艾伦方差分析工具"
VERSION="1.0.0"
DMG_NAME="${APP_NAME}_v${VERSION}"
APP_PATH="dist/${APP_NAME}.app"
DMG_DIR="dmg_temp"
DMG_FILE="dist/${DMG_NAME}.dmg"

echo "=========================================="
echo "创建 macOS DMG 安装包"
echo "=========================================="

# 检查 .app 是否存在
if [ ! -d "$APP_PATH" ]; then
    echo "错误: 找不到 $APP_PATH"
    echo "请先运行 build_mac_complete.sh 生成应用"
    exit 1
fi

# 清理旧文件
rm -rf "$DMG_DIR"
rm -f "$DMG_FILE"

# 创建临时 DMG 目录
mkdir -p "$DMG_DIR"

# 复制 .app 到临时目录
echo "复制应用..."
cp -R "$APP_PATH" "$DMG_DIR/"

# 创建应用程序快捷方式
echo "创建应用程序链接..."
ln -s /Applications "$DMG_DIR/Applications"

# 创建 README
cat > "$DMG_DIR/使用说明.txt" << EOF
艾伦方差分析工具 v${VERSION}

【安装方法】
将 ${APP_NAME}.app 拖动到 Applications 文件夹

【使用方法】
1. 打开应用
2. 选择 CO2 和/或 CH4 数据文件
3. 点击"开始分析"
4. 结果自动保存到桌面

【数据格式】
制表符分隔的文本文件：
时间戳	浓度值
2024-01-01 10:00:00	415.23

【注意事项】
首次打开可能提示"无法打开"，请按以下步骤：
1. 打开"系统偏好设置" > "安全性与隐私"
2. 点击"仍要打开"
或者在终端执行：
xattr -cr /Applications/${APP_NAME}.app

【技术支持】
如有问题请联系技术支持
EOF

# 创建 DMG
echo "创建 DMG 文件..."
hdiutil create -volname "$APP_NAME" \
    -srcfolder "$DMG_DIR" \
    -ov -format UDZO \
    "$DMG_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ DMG 创建成功！"
    echo "=========================================="
    echo "文件位置: $DMG_FILE"
    echo "文件大小: $(du -h "$DMG_FILE" | cut -f1)"
    echo ""
    echo "现在可以分发这个 DMG 文件了"
else
    echo ""
    echo "❌ DMG 创建失败"
    exit 1
fi

# 清理临时文件
echo "清理临时文件..."
rm -rf "$DMG_DIR"

echo "完成！"
