#!/bin/bash
# release.sh - 自动发布新版本到 GitHub

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "❌ 错误：未指定版本号"
    echo ""
    echo "用法: ./release.sh <版本号>"
    echo "例如: ./release.sh 1.0.1"
    echo ""
    exit 1
fi

echo "=========================================="
echo "🚀 准备发布版本 v${VERSION}"
echo "=========================================="
echo ""

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 检测到未提交的更改，正在提交..."
    git add .
    git commit -m "发布版本 v${VERSION}"
else
    echo "✅ 没有未提交的更改"
fi

# 推送到远程
echo ""
echo "📤 推送更改到远程仓库..."
git push

if [ $? -ne 0 ]; then
    echo "❌ 推送失败，请检查网络连接或仓库权限"
    exit 1
fi

# 创建并推送标签
echo ""
echo "🏷️  创建版本标签 v${VERSION}..."
git tag "v${VERSION}"
git push origin "v${VERSION}"

if [ $? -ne 0 ]; then
    echo "❌ 标签推送失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 版本 v${VERSION} 已成功发布！"
echo "=========================================="
echo ""
echo "🔄 GitHub Actions 正在自动打包..."
echo "📊 查看进度："
echo "   https://github.com/你的用户名/allan_variance_tool/actions"
echo ""
echo "⏰ 预计 5-10 分钟后完成打包"
echo ""
echo "📦 打包完成后，可在以下位置下载："
echo "   https://github.com/你的用户名/allan_variance_tool/releases/tag/v${VERSION}"
echo ""
echo "=========================================="
