from pdf2image import convert_from_path
from PIL import Image
import os

# Change the working directory to the script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 将 PDF 转换为多个 PIL 图像对象
images = convert_from_path('test2.pdf')

# 获取每个图像的宽度和高度
widths, heights = zip(*(i.size for i in images))

# 创建一个新的图像对象，宽度为最大宽度，高度为所有图像高度之和
total_height = sum(heights)
max_width = max(widths)
new_image = Image.new('RGB', (max_width, total_height))

# 将每个图像粘贴到新图像中
y_offset = 0
for image in images:
    new_image.paste(image, (0, y_offset))
    y_offset += image.height

# 保存新图像
new_image.save('output_image.jpg')