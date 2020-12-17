'''
模块导入
'''
import cv2
import time
import math
import random
import numpy as np
from PIL import Image
from skimage import transform

'''
参数整定
'''
#================================
count = 0 # 定义图片计数变量，后续用此变量来决定图片
img_count = 1 # 只截取一张图片
name_frame = '彩色照片'
name_gray = '灰度照片'
filepath = '人脸图片'
threshold = 20
#================================


class ImageProcess(object):
    '''
    变量初始化
    '''
    def __init__(self,filepath,input_name,name_frame,name_gray,width,height):
        self.filepath = filepath
        self.input_name = input_name
        self.name_frame = name_frame
        self.name_gray = name_gray
        self.width = width
        self.height = height

    '''
    人脸图片采集
    '''

    def ImageCollect(self):
        count = 0
        time.sleep(2)
        while True:
            count += 1
            ret,frame = capture.read()
            frame = cv2.cvtColor(src=frame,code=cv2.COLOR_BGR2RGB)
            # 将图像转为灰度
            gray = cv2.cvtColor(src=frame,code=cv2.COLOR_RGB2GRAY)
            # 返回图片的坐标信息
            loc_face = faceModel.detectMultiScale(frame,scaleFactor=1.2,)

            final_fname = '%s/%s的%s.jpg' % (self.filepath,self.input_name, self.name_frame)
            final_gname = '%s/%s的%s.jpg' % (self.filepath,self.input_name, self.name_gray)

            for (x,y,w,h) in loc_face:
                # cv2.rectangle(img=frame,pt1=(x,y),pt2=(x+w,y+h),color=(0,255,0),thickness=2)
                # cv2.putText(frame,self.input_name,org=(x, y - 10),fontScale=1,fontFace=cv2.FONT_HERSHEY_COMPLEX,color=(0, 255, 0),
                #             thickness=1)
                # cv2.imshow('liveface',frame)
                if count <= img_count:

                    save_frame = Image.fromarray(frame)
                    save_gray = Image.fromarray(gray)

                    save_frame.save(final_fname)
                    save_gray.save(final_gname)

            if count > img_count:
                break

        capture.release()  # 释放资源
        cv2.destroyAllWindows()  # 关闭窗口

        image = Image.open(final_gname)
        image = np.array(image)

        return image

    '''
    图片的裁剪  512*512
    '''
    def image_crop(self):
        in_image = self.ImageCollect()
        out_image = cv2.resize(in_image,(512,512))

        # out_image = in_image.resize((self.width,self.height),Image.ANTIALIAS)
        save = Image.fromarray(out_image)
        save.save('%s/%s裁剪后的%s.jpg' % (self.filepath,self.input_name,self.name_gray))

        return save


class ImageNoise(object):

    def __init__(self,image,mean,sigma,filepath,name_gray,input_name):
        self.image = np.array(image)
        self.mean = mean
        self.sigma = sigma
        self.filepath = filepath
        self.name_gray = name_gray
        self.input_name = input_name

    '''
    椒盐噪声
    '''
    def sp_noise(self,prob):

        sp_out = np.zeros(self.image.shape,dtype='uint8')
        for i in range(self.image.shape[0]):
            for j in range(self.image.shape[1]):
                rdn = random.random()
                if rdn < prob:
                    sp_out[i][j] = 0
                elif rdn > 1 - prob:
                    sp_out[i][j] = 255
                else:
                    sp_out[i][j] = self.image[i][j]
        save_sp = Image.fromarray(sp_out)
        save_sp = save_sp.convert('L')
        save_sp.save('%s/%s的加入椒盐噪声后的%s.jpg' % (self.filepath,self.input_name,self.name_gray))

        return save_sp

    '''
    高斯噪声
    '''
    def gauss_noise(self):
        image_array = np.array(self.image,dtype='float')
        noise = np.random.normal(self.mean,self.sigma**2,self.image.shape)
        gas_out = image_array + noise
        # if gas_out.min() < 0:
        #     low_clip = -1
        # else:
        #     low_clip = 0
        # gas_out = np.clip(gas_out,low_clip,1.0)
        # gas_out = np.uint8(gas_out * 255)

        save_gas = Image.fromarray(gas_out)
        save_gas = save_gas.convert('L')
        save_gas.save('%s/%s的加入高斯噪声后的%s.jpg' % (self.filepath,self.input_name,self.name_gray))

        return save_gas


class ImageFilters(object):
    def __init__(self,image,ksize,sigma,filter_size,filepath,input_name):
        self.image = np.array(image)
        self.ksize = ksize
        self.sigma = sigma
        self.filter_size = filter_size
        self.filepath = filepath
        self.input_name = input_name

    '''
    高斯滤波步骤：
    1.对图像进行边缘补0  // padding
    2.根据高斯滤波器的核大小和标准差大小实现高斯滤波器
    3.使用高斯滤波器对图像进行滤波（相乘再相加）
    4.输出高斯滤波后的图像
    '''
    def gauss_filter(self,name_noise):
        w,h = self.image.shape
        kernel = np.zeros([self.ksize,self.ksize])
        center = self.ksize // 2

        # 利用专有公式计算标准差
        if self.sigma == 0:
            sigma = ((self.ksize-1)*0.5-1)*0.3+0.8
        else:
            sigma = self.sigma
        s = 2 * (sigma**2)
        sum_val = 0
        # 卷积核的求取
        for i in range(0,self.ksize):
            for j in range(0,self.ksize):
                x = i - center
                y = j - center
                kernel[i][j] = np.exp( -(x**2 + y**2) / s)
                sum_val += kernel[i][j]
        sum_val = 1 / sum_val
        kernel = kernel * sum_val
        addLine = int((self.ksize - 1) / 2)
        # 边缘补0
        self.image = cv2.copyMakeBorder(self.image,addLine,addLine,addLine,addLine,borderType=cv2.BORDER_REPLICATE)
        source_x = addLine
        source_y = addLine
        # 开始进行卷积
        for delta_x in range(0,w):
            for delta_y in range(0,h):
                self.image[source_x,source_y] = np.sum(self.image[source_x-addLine:source_x+addLine+1,source_y-addLine:source_y+addLine+1]*kernel)
            source_x += 1
            source_y = addLine
        # 保存图片
        save = Image.fromarray(self.image[addLine:w+addLine,addLine:h+addLine])
        save = save.convert('L')
        save.save('%s/%s的经过高斯滤波后的%s.jpg' % (self.filepath,self.input_name,name_noise))

    '''
    中值滤波步骤：
    1.边缘补0
    2.构造滤波器
    3.进行空间滤波
    '''
    def median_filter(self,name_noise):
        input_image_cp = np.copy(self.image)
        pad_num = int((self.filter_size - 1) / 2)
        input_image_cp = np.pad(input_image_cp,(pad_num,pad_num),mode='constant',constant_values=0)
        w,h = input_image_cp.shape
        output_image = np.copy(input_image_cp)

        # 空间滤波
        for i in range(pad_num,w-pad_num):
            for j in range(pad_num,h-pad_num):
                output_image[i,j] = np.median(input_image_cp[i-pad_num:i+pad_num+1,j-pad_num:j+pad_num+1])

        output_image = output_image[pad_num:w-pad_num,pad_num:h-pad_num]
        # 保存图片
        save = Image.fromarray(output_image)
        save = save.convert('L')
        save.save('%s/%s的经过中值滤波后的%s.jpg' % (self.filepath,self.input_name,name_noise))

'''
sobel边缘检测算法
'''
def Sobel(image,threshold,filepath,input_name):
    gray = np.array(image)
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

    save = Image.fromarray(temp)
    save = save.convert('L')
    save.save('%s/%s的经过sobel的灰度图片.jpg' % (filepath,input_name))


'''
主函数
'''
if __name__ == '__main__':
    # 首先加载 opencv 的人脸分类器
    faceModel = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    # 输入测试者的姓名
    input_name = input('请输入姓名-->')
    # 开启摄像头，0代表内置摄像头，1代表外置
    capture = cv2.VideoCapture(0)

    image_process = ImageProcess(filepath,input_name,name_frame,name_gray,512,512)
    image = image_process.image_crop()

    image_noise = ImageNoise(image,0,6,filepath,name_gray,input_name)
    image_sp = image_noise.sp_noise(0.1)
    image_gas = image_noise.gauss_noise()

    image_filters_sp = ImageFilters(image_sp,9,0,3,filepath,input_name)
    image_filters_sp.gauss_filter('椒盐噪声')
    image_filters_sp.median_filter('椒盐噪声')

    image_filters_gas = ImageFilters(image_gas,9,1,3,filepath,input_name)
    image_filters_gas.gauss_filter('高斯噪声')
    image_filters_gas.median_filter('高斯噪声')

    Sobel(image,threshold,filepath,input_name)

