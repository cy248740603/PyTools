import cv2
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import sys
from xlrd import open_workbook # xlrd用于读取xld

bk_img = cv2.imread("bg.png")
#设置需要显示的字体
fontpath = "/Users/CY/Documents/pythonProject/阿里汉仪智能黑体.TTF"
font = ImageFont.truetype(fontpath, 32)
img_pil = Image.fromarray(bk_img)

workbook = open_workbook(r'/Users/CY/Documents/pythonProject/xls.xlsx')  # 打开xls文件
# sheet_name= workbook.sheet_names()  # 打印所有sheet名称，是个列表
sheet = workbook.sheet_by_index(0)  # 根据sheet索引读取sheet中的所有内容
# sheet1= workbook.sheet_by_name('Sheet1')  # 根据sheet名称读取sheet中的所有内容
print(sheet.name, sheet.nrows, sheet.ncols)  # sheet的名称、行数、列数
print(sheet.col_values(0))
content = sheet.col_values(0)  # 第0列内容
i = 0
for name in content:
    draw = ImageDraw.Draw(img_pil)
    #绘制文字信息
    draw.text((100, 300),  "Hello World", font = font, fill = (255, 255, 255))
    draw.text((100, 350),  name, font = font, fill = (255, 255, 255))
    i += 1
    bk_img = np.array(img_pil)
    cv2.imwrite("/Users/CY/Documents/pythonProject/" + str(i) + name + ".jpg",bk_img,[int(cv2.IMWRITE_PNG_COMPRESSION),9])
# cv2.imshow("add_text",bk_img)
# cv2.waitKey()
