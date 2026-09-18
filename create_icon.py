"""
从 PNG 创建 macOS 和 Windows 图标
需要: pip install pillow

使用方法:
    python create_icon.py your_icon.png
"""
from PIL import Image
import subprocess
import os
import sys

def create_icons(png_path):
    """从 PNG 创建 icns 和 ico"""
    if not os.path.exists(png_path):
        print(f"错误: 找不到文件 {png_path}")
        return

    img = Image.open(png_path)

    # Windows .ico
    print("创建 Windows 图标...")
    sizes_ico = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save('icon.ico', sizes=sizes_ico)
    print("✅ 已创建 icon.ico")

    # macOS .icns (需要在 Mac 上运行)
    if os.system('which iconutil') == 0:
        print("创建 macOS 图标...")
        iconset = 'icon.iconset'
        os.makedirs(iconset, exist_ok=True)

        sizes_icns = [16, 32, 64, 128, 256, 512]
        for size in sizes_icns:
            img_resized = img.resize((size, size), Image.LANCZOS)
            img_resized.save(f'{iconset}/icon_{size}x{size}.png')

            # 2x 版本
            img_resized_2x = img.resize((size * 2, size * 2), Image.LANCZOS)
            img_resized_2x.save(f'{iconset}/icon_{size}x{size}@2x.png')

        subprocess.run(['iconutil', '-c', 'icns', iconset])
        subprocess.run(['rm', '-rf', iconset])
        print("✅ 已创建 icon.icns")
    else:
        print("⚠️  需要在 macOS 上才能创建 .icns 文件")

    print("\n图标创建完成！")
    print("在 build_spec.py 中设置:")
    print("  icon='icon.ico'  # Windows")
    print("  icon='icon.icns' # macOS")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python create_icon.py <图标文件.png>")
        print("建议使用 1024x1024 的 PNG 图片")
        sys.exit(1)

    create_icons(sys.argv[1])
