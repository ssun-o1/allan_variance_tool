# 快速开始指南

## 📦 用户使用指南

### 第一次使用

#### macOS 用户
1. 双击下载的 `艾伦方差分析工具_v1.0.0.dmg`
2. 将应用拖动到 Applications 文件夹
3. 打开 Applications，找到"艾伦方差分析工具"
4. 首次打开可能提示安全警告，执行以下命令：
   ```bash
   xattr -cr /Applications/艾伦方差分析工具.app
   ```
5. 重新打开应用即可使用

#### Windows 用户

**安装版**:
1. 双击 `艾伦方差分析工具_v1.0.0_Setup.exe`
2. 按照向导完成安装
3. 从桌面或开始菜单启动程序

**便携版**:
1. 解压 `艾伦方差分析工具_v1.0.0_便携版.zip`
2. 双击 `艾伦方差分析工具.exe`
3. 首次运行可能被 SmartScreen 拦截，点击"更多信息" → "仍要运行"

### 分析数据

1. **准备数据文件**
   - 文件格式：`.txt` 文件
   - 内容：时间戳 + Tab + 浓度值
   - 示例：
     ```
     2024-01-01 10:00:00	415.23
     2024-01-01 10:00:03	415.25
     ```

2. **运行分析**
   - 打开应用
   - 点击"选择文件"选择 CO2 或 CH4 数据文件
   - 点击"开始分析"
   - 等待几秒到几十秒

3. **查看结果**
   - 自动在桌面生成 Excel 文件
   - 文件名：`艾伦方差分析结果_时间戳.xlsx`
   - 包含原始数据、分析结果和图表

---

## 🔧 开发者打包指南

### macOS 打包步骤

#### 1. 准备环境
```bash
# 确保安装了 Python 3.8+
python3 --version

# 进入项目目录
cd ~/Desktop/allan_variance_tool
```

#### 2. 执行打包
```bash
# 给脚本执行权限
chmod +x build_mac_complete.sh create_dmg.sh

# 一键打包
./build_mac_complete.sh
```

#### 3. 测试应用
```bash
# 运行测试
open dist/艾伦方差分析工具.app
```

#### 4. 分发
- DMG 文件位置：`dist/艾伦方差分析工具_v1.0.0.dmg`
- 直接分发这个 DMG 文件给用户

#### 可选：添加自定义图标
```bash
# 1. 准备一个 1024x1024 的 PNG 图标
# 2. 生成图标文件
python create_icon.py your_icon.png

# 3. 修改 build_spec.py
# 将 icon=None 改为 icon='icon.icns'

# 4. 重新打包
./build_mac_complete.sh
```

### Windows 打包步骤

#### 方式一：创建安装程序

1. **安装 Inno Setup**
   - 下载：https://jrsoftware.org/isdl.php
   - 安装到默认位置

2. **执行打包**
   ```batch
   build_windows_complete.bat
   ```

3. **生成的文件**
   - `dist\艾伦方差分析工具.exe` - 可执行文件
   - `dist\艾伦方差分析工具_v1.0.0_Setup.exe` - 安装程序

#### 方式二：创建便携版

1. **执行打包**
   ```batch
   build_windows_portable.bat
   ```

2. **生成的文件**
   - `dist\艾伦方差分析工具_v1.0.0_便携版.zip`

### 打包常见问题

#### macOS

**Q: 打包时提示 "command not found: python3"**
```bash
# 安装 Python 3
brew install python3
```

**Q: 打包失败，提示缺少某个库**
```bash
# 清理并重新安装
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller
```

**Q: DMG 创建失败**
```bash
# 手动创建 DMG
hdiutil create -volname "艾伦方差分析工具" \
    -srcfolder "dist/艾伦方差分析工具.app" \
    -ov -format UDZO \
    "dist/艾伦方差分析工具_v1.0.0.dmg"
```

#### Windows

**Q: 提示 "python 不是内部或外部命令"**

A: 安装 Python 并添加到 PATH
- 下载：https://www.python.org/downloads/
- 安装时勾选 "Add Python to PATH"

**Q: 打包后的 exe 文件过大**

A: 这是正常的，PyInstaller 会打包所有依赖库
- 单文件模式：约 80-150MB
- 可以使用 UPX 压缩（有风险）

**Q: 杀毒软件报毒**

A: 这是误报，可以：
1. 添加到白名单
2. 使用代码签名证书（需要购买）

### 版本更新流程

1. **修改版本号**
   - `build_mac_complete.sh`: 修改 `VERSION="1.0.0"`
   - `build_windows_complete.bat`: 修改文件中的版本号
   - `installer.iss`: 修改 `#define MyAppVersion "1.0.0"`
   - `README.md`: 更新版本号和更新日志

2. **重新打包**
   ```bash
   # macOS
   ./build_mac_complete.sh

   # Windows
   build_windows_complete.bat
   ```

3. **测试新版本**
   - 在干净的系统上测试安装和运行
   - 验证所有功能正常工作

4. **发布**
   - 上传到分发服务器
   - 通知用户更新

---

## 📝 测试清单

### 功能测试
- [ ] 选择 CO2 文件能正常加载
- [ ] 选择 CH4 文件能正常加载
- [ ] 同时选择两个文件能正常处理
- [ ] 文件格式错误时有友好提示
- [ ] 分析结果正确保存到桌面
- [ ] Excel 文件包含所有必要的 Sheet
- [ ] 图表正确显示

### 平台测试
- [ ] macOS 10.13+ 正常运行
- [ ] macOS 首次打开提示处理正确
- [ ] Windows 10 正常运行
- [ ] Windows SmartScreen 提示处理正确

### 安装测试
- [ ] macOS DMG 正常挂载和安装
- [ ] Windows 安装程序正常安装和卸载
- [ ] Windows 便携版解压后正常运行
- [ ] 桌面快捷方式正常工作

---

## 🎯 性能优化建议

### 减小安装包体积

1. **排除不必要的模块**
   在 `build_spec.py` 中添加：
   ```python
   excludes=[
       'matplotlib.tests',
       'numpy.tests',
       'pandas.tests',
   ]
   ```

2. **使用 UPX 压缩**
   ```bash
   # macOS
   brew install upx
   pyinstaller build_spec.py --upx-dir=/usr/local/bin

   # Windows
   # 下载 UPX 并添加到 PATH
   pyinstaller build_spec.py --upx-dir=C:\upx
   ```

### 提升启动速度

1. **使用目录模式而非单文件模式**
   在 `build_spec.py` 中修改 `EXE` 配置

2. **减少导入的库**
   只导入必要的模块

---

## 📞 支持与反馈

如有问题或建议，请联系技术支持团队。
