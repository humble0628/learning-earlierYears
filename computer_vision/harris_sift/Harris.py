'''
参数整定
'''
#=============================
sigma = 6
image_name = 'harris.jpg'
filepath = 'save_harris'
define_name = 'harris.gif'
#=============================

'''
模块导入
'''
import os
import cv2
import math
import imageio
import numpy as np
from PIL import Image

'''
功能函数
'''
class Process(object):

    # 四舍五入取整
    def fix(self,in_num):
        out_num = (int)(in_num + 0.5)
        return out_num

    # 求矩阵的转置
    def transfor(self,matrix):
        # if not matrix: return matrix
        row,col = len(matrix),len(matrix[0])
        res = []
        for i in range(col):
            temp = []
            for j in range(row):
                temp.append(matrix[j][i])
            res.append(temp)
        return np.array(res)

    # 高斯滤波
    # k_size为高斯核的大小，sigma为标准差
    def gauss_filter(self,k_size,sigma):
        kernel = np.zeros([k_size,k_size])
        center = k_size // 2
        s = 2 * (sigma**2)
        sum = 0
        for i in range(0,k_size):
            for j in range(0,k_size):
                x = i - center
                y = j - center
                kernel[i][j] = np.exp( - (x**2 + y**2) / s)
                sum += kernel[i][j]
        # 对生成的高斯核进行归一化，即所有数的总和为1
        sum = 1 / sum
        kernel *= sum
        return kernel

    # padding
    def padding(self,kernel,out_shape):
        # valid表示不对边缘做任何处理，直接用原图像
        if out_shape == 'valid':
            return (0,0),(0,0)
        elif out_shape == 'same':
            h,w = kernel.shape
            # 以下分别表示在四个方向需要扩增的行数
            # 所谓same，就是当过滤器与边缘像素进行卷积后，将结果落在原图像的边缘，使得卷积后图片的shape不变
            # floor的功能是向下取整，ceil的功能是向上取整，之所以采用这种方式，主要是为了解决kernel的shape中存在偶数的过滤器
            pad_h1 = int(math.floor((h - 1) / 2))
            pad_h2 = int(math.ceil((h - 1) / 2))
            pad_w1 = int(math.floor((w - 1) / 2))
            pad_w2 = int(math.ceil((w - 1) / 2))
            return (pad_h1,pad_h2),(pad_w1,pad_w2)

    # 卷积
    def convlution2d(self,image,kernel,out_shape):
        h,w = kernel.shape
        (pad_h1,pad_h2),(pad_w1,pad_w2) = self.padding(kernel,out_shape)
        # 完成边缘补0,分别对应上下左右
        in_image = np.lib.pad(image,((pad_h1,pad_h2),(pad_w1,pad_w2)),mode='constant')

        # 卷积
        # 这里要对补0后的新图进行卷积操作，但是卷积后的图需要和原图一样大小
        temp = []
        out_image = []
        for i in range(0,in_image.shape[0]-h+1):
            for j in range(0,in_image.shape[1]-w+1):
                temp.append(np.sum(np.multiply(in_image[i:i+h,j:j+w],kernel)))
            out_image.append(temp)
            temp = []

        return np.array(out_image)

'''
Harris
'''
class Harris(object):
    def __init__(self,image_name):
        self.image_name = image_name

    # 图片处理包括图片的读取，彩色转灰度，以及修剪图片的尺寸
    def image_process(self):
        in_image = cv2.imread(self.image_name)
        out_image = cv2.resize(in_image, (512, 512))
        gray = cv2.cvtColor(out_image,code=cv2.COLOR_RGB2GRAY)

        self.img = out_image
        self.gray = np.array(gray)
        self.h = self.gray.shape[0]
        self.w = self.gray.shape[1]

        return np.array(gray)

    # 计算图片的两个方向的像素梯度，写完后发现老师的代码里给了，索性用老师给的方法，
    def calGrandient(self):
        self.sharp = self.gray
        GradientX = self.gray
        GradientY = self.gray
        for i in range(0,self.h):
            for j in range(0,self.w):
                if i < self.h-1 and j < self.w-1:
                    dx = abs(int(self.gray[i,j+1]) - int(self.gray[i,j]))
                    dy = abs(int(self.gray[i+1,j]) - int(self.gray[i,j]))

                    GradientX[i,j] = dx
                    GradientY[i,j] = dy
                    self.sharp[i,j] = max(dx,dy)
                else:
                    GradientX[i, j] = 0
                    GradientY[i, j] = 0
                    self.sharp[i, j] = 0

        self.Ix = np.array(GradientX)
        self.Iy = np.array(GradientY)

    # 按照公式计算R值，
    def calR(self,lx2,ly2,lxy):
        # R = detM - K(traceM)**2

        R = np.zeros(self.gray.shape)
        for i in range(self.h):
            for j in range(self.w):
                M = np.array([[lx2[i,j],lxy[i,j]],[lxy[i,j],ly2[i,j]]])

                R[i,j] = np.linalg.det(M) - 0.06*(np.trace(M))*(np.trace(M))

        self.R = R
    # 根据阈值生成相应的灰度图片
    def R_threshold(self,threshold):
        final_R = self.R
        R = self.R
        for i in range(self.h):
            for j in range(self.w):
                if R[i,j] < threshold:
                    final_R[i,j] = 255
                    cv2.circle(self.img,(i,j),1,(255,0,0),0)
        return final_R

    def R_gif(self,filepath,define_name):
        # 首先以5为步长生成0-100的20张不同阈值的图片
        # 图片保存时的名称以阈值开头
        list = np.linspace(0,20,21)
        for threshold in list:
            image = self.R_threshold(threshold)
            save = Image.fromarray(image)
            save = save.convert('L')
            save.save('%s/%d_harris.jpg' % (filepath,int(threshold * 10)))

        # 由于listdir返回的数组是无序的，按照阈值大小从小到大排列，以便清楚的查看动态图效果
        name = os.listdir(filepath)
        name_sort = []
        name_res = ''
        for i in name:
            name_sort.append(int(i.split('_')[0]))
            name_res = '_' + str(i.split('_')[1])

        name_sort.sort()
        for i in range(len(name_sort)):
            name_sort[i] = str(name_sort[i]) + name_res

        # imageio库在使用时，必须包含图片的父路径，因此在之前名字的基础上加上父路径
        temp = [filepath+'/'] * len(name_sort)
        out_name = []
        for i in range(len(name_sort)):
            out_name.append(temp[i] + name_sort[i])

        # 生成并保存动态图
        save = []
        for image in out_name:
            im = imageio.imread(image)
            save.append(im)

        imageio.mimsave(define_name, save, 'GIF', duration=0.3)

'''
主函数
'''
if __name__ == '__main__':
    P = Process()
    H = Harris(image_name)

    dy = np.array([[-1,0,1],
                   [-1,0,1],
                   [-1,0,1]])
    # dx为dy的转置
    dx = P.transfor(dy)
    # 对输入的图片进行处理，包括彩色转灰度，尺寸修剪
    bw = H.image_process()
    print(bw.shape)
    # 计算生成图片在x、y方向的梯度矩阵
    lx = P.convlution2d(bw,dx,'same')
    ly = P.convlution2d(bw,dy,'same')
    # 生成高斯卷积核
    g = P.gauss_filter(k_size=max(1,P.fix(6*sigma)),sigma=sigma)

    # 利用卷积生成M矩阵所需要的元素
    lx2 = P.convlution2d(lx**2,g,'same')
    ly2 = P.convlution2d(ly**2,g,'same')
    lxy = P.convlution2d(lx*ly,g,'same')

    H.calR(lx2,ly2,lxy)
    # 将阈值以5为步长，依次保存阈值为0-20的21张图片，并将渐变的20张图片生成动态图
    H.R_gif(filepath,define_name)