'''
模块导入
'''
from PIL import Image
import numpy as np
import math
import os
import cv2
import imageio

'''
参数整定
'''
#================================
image = Image.open('人脸图片/nuonuo.jpg')
filepath = 'nuo/'
out_name = 'nuo.gif'
#================================

def Sobel(image,threshold,filepath,input_name):
    frame = np.array(image)
    gray = cv2.cvtColor(src=frame,code=cv2.COLOR_RGB2GRAY)
    w,h = gray.shape
    temp = np.zeros((w,h),dtype='uint8')
    for i in range(0,w-2):
        for j in range(0,h-2):
            # 计算x y方向的梯度
            gy = gray[i, j] * 1 + gray[i, j + 1] * 2 + gray[i, j + 2] * 1 - gray[i + 2, j] * 1 - gray[
                i + 2, j + 1] * 2 - gray[i + 2, j + 2] * 1
            gx = gray[i, j] * 1 + gray[i + 1, j] * 2 + gray[i + 2, j] * 1 - gray[i, j + 2] * 1 - gray[
                i + 1, j + 2] * 2 - gray[i + 2, j + 2] * 1
            grad = math.sqrt(gx * gx + gy * gy)
            if grad > threshold:
                temp[i,j] = 255
            else:
                temp[i,j] = 0
    save = cv2.cvtColor(temp,code=cv2.COLOR_GRAY2RGB)
    save = Image.fromarray(save)
    save = save.convert('RGB')
    save.save('%s/%d_%s的经过sobel的彩色图片.jpg' % (filepath,threshold,input_name))

def ComposeGif(out_name,filepath):
    in_name = os.listdir(filepath)
    name_sort = []
    name_add = ''
    # 将返回的子文件名按照阈值从小到大进行排列
    for i in in_name:
        name_sort.append(int(i.split('_')[0]))
        name_add = '_' + str(i.split('_')[1])

    name_sort.sort()
    for i in range(len(in_name)):
        name_sort[i] = str(name_sort[i]) + name_add

    # 将排序后的文件名的前面加上 filepath/ 以便imageio读取
    temp = [filepath] * len(name_sort)
    out_image = []
    for i in range(len(name_sort)):
        out_image.append(temp[i] + name_sort[i])

    out_image.append('人脸图片/nuonuo.jpg')
    print(out_image)

    save = []
    for image in out_image:
        im = imageio.imread(image)
        save.append(im)

    imageio.mimsave(out_name,save,'GIF',duration=0.3)

if __name__ == '__main__':
    # for threshold in range(0,42,3):
    #     Sobel(image,threshold,filepath,'mom')

    ComposeGif(out_name,filepath)
