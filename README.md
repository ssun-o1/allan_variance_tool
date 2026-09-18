# 艾伦方差分析工具

## 📦 分发包说明

### macOS
- **文件格式**: DMG 磁盘映像
- **安装方法**: 双击 DMG → 拖动到 Applications 文件夹
- **文件名**: 艾伦方差分析工具_v1.0.0.dmg

### Windows
- **安装版**: 双击 Setup.exe 自动安装
- **便携版**: 解压 zip 直接运行 .exe

## ✨ 功能特点
- ✅ 自动计算 Overlapping Allan Variance
- ✅ 支持 CO2 / CH4 双气体分析
- ✅ 结果自动保存到桌面
- ✅ 生成 Excel 报告和图表
- ✅ 无需安装 Python 环境

## 🚀 使用方法

1. **启动程序**
   - macOS: 打开 Applications 中的应用
   - Windows: 双击桌面或开始菜单的快捷方式

2. **选择数据文件**
   - 点击"选择文件"按钮
   - 至少选择一个气体的数据文件（CO2 或 CH4）

3. **开始分析**
   - 点击"开始分析"按钮
   - 等待处理完成（通常几秒到几十秒）

4. **查看结果**
   - 结果自动保存到桌面
   - 文件名: `艾伦方差分析结果_时间戳.xlsx`

## 📄 数据格式要求

文件格式：制表符分隔的 `.txt` 文件

```
2024-01-01 10:00:00	415.23
2024-01-01 10:00:03	415.25
2024-01-01 10:00:06	415.21
...
```

**格式说明**:
- 两列数据：时间戳 + 浓度值
- 分隔符：制表符（Tab）
- 时间格式：`YYYY-MM-DD HH:MM:SS`

## ⚠️ 常见问题

### macOS

**Q: 提示"无法打开，因为它来自身份不明的开发者"**

A: 两种解决方法：

方法一（推荐）:
```bash
# 在终端执行
xattr -cr /Applications/艾伦方差分析工具.app
```

方法二:
1. 打开"系统偏好设置" > "安全性与隐私"
2. 点击"仍要打开"

### Windows

**Q: 提示 Windows SmartScreen 已阻止**

A: 点击"更多信息" → "仍要运行"

**Q: 杀毒软件报毒**

A: 这是误报，因为 PyInstaller 打包的程序经常被误报。可以添加信任或暂时关闭杀毒软件。

## 🔧 开发者打包说明

### macOS 打包

```bash
# 给脚本执行权限
chmod +x build_mac_complete.sh create_dmg.sh

# 一键打包（生成 .app 和 .dmg）
./build_mac_complete.sh
```

生成文件:
- `dist/艾伦方差分析工具.app` - 应用程序
- `dist/艾伦方差分析工具_v1.0.0.dmg` - DMG 安装包

### Windows 打包

**方式一：安装程序（需要先安装 Inno Setup）**
```batch
# 下载 Inno Setup: https://jrsoftware.org/isdl.php
build_windows_complete.bat
```

**方式二：便携版**
```batch
build_windows_portable.bat
```

生成文件:
- `dist/艾伦方差分析工具.exe` - 可执行文件
- `dist/艾伦方差分析工具_v1.0.0_Setup.exe` - 安装程序（方式一）
- `dist/艾伦方差分析工具_v1.0.0_便携版.zip` - 便携版（方式二）

## 📊 输出文件说明

Excel 文件包含以下 Sheet:
- `CO2_原始数据` - CO2 原始数据和时间戳
- `CO2_艾伦偏差结果` - CO2 分析结果
- `CH4_原始数据` - CH4 原始数据和时间戳
- `CH4_艾伦偏差结果` - CH4 分析结果
- `图表` - 艾伦偏差折线图

## 💻 系统要求
- **macOS**: 10.13 (High Sierra) 或更高
- **Windows**: Windows 10 或更高
- **硬盘空间**: 至少 200MB

## 📁 项目结构

```
allan_variance_tool/
├── allan_variance_gui.py          # 主程序
├── requirements.txt                # Python 依赖
├── build_spec.py                  # PyInstaller 配置
├── build_mac_complete.sh          # macOS 完整打包脚本
├── create_dmg.sh                  # 创建 DMG 脚本
├── build_windows_complete.bat     # Windows 完整打包
├── build_windows_portable.bat     # Windows 便携版打包
├── installer.iss                  # Inno Setup 配置
└── README.md                      # 本文件
```

## 🛠️ 依赖说明

本项目使用以下 Python 库：
- numpy 1.24.3 - 数值计算
- pandas 2.0.3 - 数据处理
- openpyxl 3.1.2 - Excel 文件操作
- matplotlib 3.7.2 - 图表绘制
- Pillow 10.0.0 - 图像处理

## 📧 技术支持

如有问题请联系技术支持

## 📝 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- ✅ 支持 CO2 和 CH4 数据分析
- ✅ GUI 界面
- ✅ 自动保存到桌面
- ✅ 跨平台支持（macOS 和 Windows）

## 📄 许可证

本项目仅供内部使用
