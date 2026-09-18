# 跨平台打包指南

## 🎯 在 macOS 上打包 Windows 版本

由于 PyInstaller 只能在目标平台上打包，直接在 macOS 上打包 Windows 版本会遇到兼容性问题。以下是推荐的解决方案：

---

## 🥇 方案一：GitHub Actions（推荐）

### 优点
✅ 完全免费（公开仓库）  
✅ 自动化，无需手动操作  
✅ 同时打包 macOS 和 Windows  
✅ 不需要本地 Windows 环境  
✅ 自动创建 Release 并上传文件

### 使用步骤

#### 1. 初始化 Git 仓库
```bash
cd ~/Desktop/allan_variance_tool

# 初始化仓库
git init
git add .
git commit -m "初始提交：艾伦方差分析工具"
```

#### 2. 创建 GitHub 仓库
1. 访问 https://github.com/new
2. 创建新仓库（可以是私有或公开）
3. 不要初始化 README、.gitignore 或 license

#### 3. 推送代码到 GitHub
```bash
# 关联远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/allan_variance_tool.git
git branch -M main
git push -u origin main
```

#### 4. 触发自动打包

**方法一：创建标签触发**
```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0
```

**方法二：手动触发**
1. 进入 GitHub 仓库
2. 点击 "Actions" 选项卡
3. 选择 "打包多平台应用" workflow
4. 点击 "Run workflow"

#### 5. 下载打包结果
1. 等待 Actions 完成（约 5-10 分钟）
2. 在 "Actions" 页面下载构建产物
3. 或在 "Releases" 页面下载发布文件

---

## 🥈 方案二：使用虚拟机

### A. 使用 UTM（macOS 原生虚拟机，免费）

#### 1. 安装 UTM
```bash
# 使用 Homebrew 安装
brew install --cask utm
```

或从官网下载：https://mac.getutm.app/

#### 2. 安装 Windows 虚拟机
1. 下载 Windows 10/11 ISO（从微软官网）
2. 在 UTM 中创建新虚拟机
3. 分配至少 4GB 内存、40GB 磁盘空间
4. 安装 Windows

#### 3. 在虚拟机中打包
1. 将项目文件夹复制到虚拟机
2. 安装 Python 3.10+
3. 运行 `build_windows_complete.bat`

### B. 使用 Parallels Desktop（付费，性能最好）

1. 安装 Parallels Desktop（$99.99/年）
2. 安装 Windows 虚拟机
3. 在虚拟机中执行打包脚本

### C. 使用 VirtualBox（免费，但性能较差）

```bash
# 安装 VirtualBox
brew install --cask virtualbox
```

1. 下载 Windows ISO
2. 创建虚拟机
3. 安装 Windows 并打包

---

## 🥉 方案三：云服务器临时打包

### A. 使用 AWS EC2（按量付费）

```bash
# 启动 Windows Server 实例（约 $0.3/小时）
# 1. 登录 AWS 控制台
# 2. 启动 EC2 Windows Server 实例
# 3. 使用 RDP 连接
# 4. 上传项目文件
# 5. 执行打包
# 6. 下载结果，终止实例
```

### B. 使用 Azure 虚拟机

类似 AWS，提供 Windows Server 实例

### C. 使用腾讯云/阿里云

国内云服务商，操作类似

---

## ❌ 不推荐：使用 Wine

虽然技术上可行，但不推荐：

```bash
# 安装 Wine
brew install --cask wine-stable

# 安装 Windows Python（通过 Wine）
# 这种方法非常不稳定，容易失败
```

**为什么不推荐：**
- PyInstaller 在 Wine 下经常失败
- 打包的 exe 可能有兼容性问题
- 调试困难

---

## 📊 方案对比详细表

| 方案 | 成本 | 时间 | 自动化 | 稳定性 | 学习曲线 |
|------|------|------|--------|--------|----------|
| GitHub Actions | 免费 | 5-10分钟 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| UTM 虚拟机 | 免费 | 1-2小时 | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Parallels | $99/年 | 30分钟 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| VirtualBox | 免费 | 2-3小时 | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 云服务器 | $0.3/小时 | 30分钟 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Wine | 免费 | 未知 | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 我的推荐

### 如果你是...

**个人开发者，偶尔打包：**
→ 使用 **GitHub Actions**（免费自动化）

**需要频繁测试打包：**
→ 使用 **UTM 虚拟机**（免费，本地控制）

**预算充足，追求效率：**
→ 使用 **Parallels Desktop**（性能最佳）

**临时需求，不想装虚拟机：**
→ 使用 **云服务器**（用完即删）

---

## 📝 GitHub Actions 详细使用说明

### 1. 项目配置

已经为你创建了 `.github/workflows/build.yml` 文件，包含：
- ✅ Windows 自动打包
- ✅ macOS 自动打包
- ✅ 自动创建便携版 ZIP
- ✅ 自动创建 DMG
- ✅ 自动发布 Release

### 2. 触发方式

**自动触发（推荐）：**
```bash
# 发布新版本时
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions 会自动：
# 1. 在 Windows 上打包 .exe
# 2. 在 macOS 上打包 .dmg
# 3. 创建 Release
# 4. 上传所有文件
```

**手动触发：**
1. GitHub 仓库 → Actions
2. 选择 "打包多平台应用"
3. 点击 "Run workflow"
4. 选择分支
5. 点击 "Run workflow" 按钮

### 3. 下载结果

**从 Actions 下载：**
1. 进入 Actions 页面
2. 点击完成的 workflow run
3. 下载 "windows-build" 和 "macos-build" artifacts

**从 Releases 下载：**
1. 进入 Releases 页面
2. 找到对应版本
3. 下载附件中的 .zip 和 .dmg

### 4. 本地测试 GitHub Actions

```bash
# 安装 act 工具（可选）
brew install act

# 本地模拟运行 GitHub Actions
act -j build-windows
act -j build-macos
```

---

## 🛠️ 实用脚本：自动化发布

创建一个便捷的发布脚本：

```bash
#!/bin/bash
# release.sh - 自动发布新版本

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "用法: ./release.sh 版本号"
    echo "例如: ./release.sh 1.0.1"
    exit 1
fi

echo "准备发布版本 v${VERSION}"

# 更新版本号（可选）
# sed -i '' "s/VERSION=.*/VERSION=\"${VERSION}\"/" build_mac_complete.sh

# 提交更改
git add .
git commit -m "发布版本 v${VERSION}"
git push

# 创建标签
git tag "v${VERSION}"
git push origin "v${VERSION}"

echo "✅ 版本 v${VERSION} 已推送"
echo "GitHub Actions 正在自动打包..."
echo "查看进度: https://github.com/你的用户名/allan_variance_tool/actions"
```

使用方法：
```bash
chmod +x release.sh
./release.sh 1.0.1
```

---

## 💡 总结

**最简单：** GitHub Actions（推荐给所有人）  
**最灵活：** UTM 虚拟机（适合开发者）  
**最快速：** Parallels Desktop（有预算就用这个）

对于你的项目，我强烈推荐使用 **GitHub Actions**，因为：
1. 完全免费
2. 零配置（我已经写好了配置文件）
3. 自动化（推送标签即可）
4. 可靠（官方环境）

现在你可以直接使用 GitHub Actions 工作流来同时打包两个平台的应用！
