"""
创建启动画面图片
"""
from PIL import Image, ImageDraw, ImageFont
import os

# 创建 640x400 的图片，深色背景
width, height = 640, 400
img = Image.new('RGB', (width, height), color='#0A0D12')
draw = ImageDraw.Draw(img)

# 绘制渐变背景效果（简化版：中心亮一些）
for y in range(height):
    for x in range(width):
        # 计算到中心的距离
        dx = (x - width/2) / width
        dy = (y - height/2) / height
        dist = (dx*dx + dy*dy) ** 0.5

        # 根据距离调整颜色（中心更亮）
        factor = max(0, 1 - dist * 1.2)
        r = int(10 + factor * 6)
        g = int(13 + factor * 10)
        b = int(18 + factor * 15)

        img.putpixel((x, y), (r, g, b))

# 绘制主标题
try:
    # 尝试使用系统中文字体
    import platform
    system = platform.system()
    if system == "Darwin":  # macOS
        title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 48)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 20)
    elif system == "Windows":
        title_font = ImageFont.truetype("msyh.ttc", 48)  # 微软雅黑
        subtitle_font = ImageFont.truetype("arial.ttf", 20)
    else:
        raise Exception("Unknown system")
except Exception as e:
    print(f"无法加载字体: {e}，使用大字体绘制英文标题")
    title_font = None
    subtitle_font = None

# 主标题
if title_font:
    title_text = "艾伦方差分析工具"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = height // 2 - 60
    draw.text((title_x, title_y), title_text, fill='#E8F5FE', font=title_font)
else:
    # 使用英文大标题
    title_text = "Allan Variance Tool"
    title_font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 42)
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font_large)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = height // 2 - 50
    draw.text((title_x, title_y), title_text, fill='#E8F5FE', font=title_font_large)
    subtitle_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)

# 副标题
subtitle_text = "Allan Variance Analysis Tool"
subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
subtitle_x = (width - subtitle_width) // 2
subtitle_y = title_y + 70

draw.text((subtitle_x, subtitle_y), subtitle_text, fill='#38BDF8', font=subtitle_font)

# 加载提示
loading_text = "正在启动..."
loading_bbox = draw.textbbox((0, 0), loading_text, font=subtitle_font)
loading_width = loading_bbox[2] - loading_bbox[0]
loading_x = (width - loading_width) // 2
loading_y = height - 80

draw.text((loading_x, loading_y), loading_text, fill='#6B7280', font=subtitle_font)

# 绘制装饰性的圆点
accent_color = '#38BDF8'
for i in range(3):
    x = width // 2 - 30 + i * 30
    y = height - 45
    draw.ellipse([x-4, y-4, x+4, y+4], fill=accent_color)

# 保存
img.save('splash.png')
print("启动画面已创建: splash.png")
