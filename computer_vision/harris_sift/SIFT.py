'''
参数整定
'''
#===================
img_count = 1
filepath = 'sift_img'
#===================

'''
模块导入
'''
import cv2
import numpy as np
from PIL import Image

'''
人脸照片读取与处理
'''
class ImageAll(object):
    def __init__(self,filepath):
        self.filepath = filepath

    def imgCollect(self):
        # 首先加载 opencv 的人脸分类器
        faceModel = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
        # 输入测试者的姓名
        # input_name = input('请输入姓名-->')
        # 开启摄像头，0代表内置摄像头，1代表外置
        capture = cv2.VideoCapture(0)
        count = 0
        while True:
            count += 1
            ret, frame = capture.read()
            frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2RGB)
            # 将图像转为灰度
            gray = cv2.cvtColor(src=frame, code=cv2.COLOR_RGB2GRAY)
            # 返回图片的坐标信息
            loc_face = faceModel.detectMultiScale(frame, scaleFactor=1.2, )

            final_fname = '%s/%s.jpg' % (self.filepath, 'RGB')
            final_gname = '%s/%s.jpg' % (self.filepath, 'GRAY')

            for (x, y, w, h) in loc_face:
                # cv2.rectangle(img=frame,pt1=(x,y),pt2=(x+w,y+h),color=(0,255,0),thickness=2)
                # cv2.putText(frame,self.input_name,org=(x, y - 10),fontScale=1,fontFace=cv2.FONT_HERSHEY_COMPLEX,color=(0, 255, 0),
                #             thickness=1)
                # cv2.imshow('liveface',frame)
                if count <= img_count:
                    # 将numpy数组转化成图片
                    save_frame = Image.fromarray(frame)
                    save_gray = Image.fromarray(gray)
                    # 图片的保存
                    save_frame.save(final_fname)
                    save_gray.save(final_gname)

            if count > img_count:
                break

        capture.release()  # 释放资源
        cv2.destroyAllWindows()  # 关闭窗口

        image = Image.open(final_fname)
        image = np.array(image)

        # 最后返回灰度图片的numpy数组形式
        return image,final_fname

    def imgProcess(self):
        image,in_name = self.imgCollect()
        rows, cols, channel = image.shape
        # 1.将图片旋转90度并保存
        M = cv2.getRotationMatrix2D((rows/2, cols/2), 45, 1)
        img45 = cv2.warpAffine(image, M, (cols, rows))
        img45 = Image.fromarray(img45)
        img45 = img45.convert('RGB')
        name1 = str(in_name.split('.')[0]) + '_spin' + '.jpg'
        img45.save(name1)
        # 2.将图片镜像处理
        img_mirror = cv2.flip(image,1)
        img_mirror = Image.fromarray(img_mirror)
        img_mirror = img_mirror.convert('RGB')
        name2 = str(in_name.split('.')[0]) + '_mirror' + '.jpg'
        img_mirror.save(name2)
        # 3.将图片放大1.2倍
        img_reduce = cv2.resize(image,((int)(rows/1.2),(int)(cols/1.2)))
        img_reduce = Image.fromarray(img_reduce)
        img_reduce = img_reduce.convert('RGB')
        name3 = str(in_name.split('.')[0]) + '_reduce' + '.jpg'
        img_reduce.save(name3)

        # 这里返回原图和旋转后的图片名，以便后续使用
        return name1,in_name

'''
ORB
'''
def ORB(name1,name2):
    # 调用opencv的orb库
    orb = cv2.ORB_create()

    img1 = cv2.imread(name1)
    img1 = cv2.cvtColor(img1,code=cv2.COLOR_BGR2RGB)
    # des是描述子
    kp1,des1 = orb.detectAndCompute(img1,None)

    img2 = cv2.imread(name2)
    img2 = cv2.cvtColor(img2,code=cv2.COLOR_BGR2RGB)
    kp2,des2 = orb.detectAndCompute(img2,None)

    # 在两张图片中画特征点
    img3 = cv2.drawKeypoints(img1,kp1,img1,color=(255,0,255))
    img4 = cv2.drawKeypoints(img2,kp2,img2,color=(255,0,255))

    # 将画点的两张图片进行横向拼接
    hmerge = np.hstack((img3,img4))
    # 转RGB进行图片保存
    save1 = Image.fromarray(hmerge)
    save1= save1.convert('RGB')
    save1.save('点.jpg')

    # 调用opencv的bf库
    bf = cv2.BFMatcher()
    # 利用knn进行点匹配
    matches = bf.knnMatch(des1,des2,k=2)

    # 调整ritio
    good = []
    for m,n in matches:
        if m.distance < 0.75*n.distance:
            good.append([m])
    # 进行连线
    img5 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,good,None,flags=2)

    save2 = Image.fromarray(img5)
    save2 = save2.convert('RGB')
    save2.save('匹配.jpg')


'''
主函数
'''
if __name__ == '__main__':
    # 进行图片的采集
    # 三种处理：旋转45度，镜像，缩小1.2倍
    I = ImageAll(filepath)
    source,image_spin = I.imgProcess()

    ORB(source,image_spin)

