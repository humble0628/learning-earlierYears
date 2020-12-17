'''
参数整定
'''
#==========================
img_left = 'Left.jpg'
img_right = 'Right.jpg'
#==========================

'''
模块导入
'''
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

'''
取点函数，返回坐标列表
'''
def getpoints(img1,img2,num):
    img1_ = Image.open(img1)
    img1_ = np.array(img1_)
    plt.imshow(img1_)
    pos1 = plt.ginput(num)

    img2_ = Image.open(img2)
    img2_ = np.array(img2_)
    plt.imshow(img2_)
    pos2 = plt.ginput(num)

    return np.array(pos1),np.array(pos2)

'''
齐次坐标转换函数
'''
def homogen(matrix):
    temp = []
    out = []
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            temp.append(matrix[i][j])
        temp.append(1)
        out.append(temp)
        temp = []

    return np.array(out)

'''
描点图片拼接连线
'''
def montage(img1,img2):
    im1 = Image.open(img1)
    im2 = Image.open(img2)
    in_im = np.hstack((im1,im2))
    plt.imshow(in_im)
    pos = np.array(plt.ginput(8))
    for i in range(pos.shape[0]):
        cv2.cvtColor(in_im,cv2.COLOR_BGR2RGB)
        in_im = cv2.circle(in_im,(int(pos[i,0]),int(pos[i,1])),3,(255,0,0),-1)
    for i in range(4):
        cv2.line(in_im,(int(pos[i,0]),int(pos[i,1])),(int(pos[i+4,0]),int(pos[i+4,1])),(0,0,255),2)

        out_im = Image.fromarray(in_im)
        out_im.save('both.jpg')

'''
单应性矩阵计算函数
'''
def DIL(uvBase,uvTrans):
    A = []
    T = []
    for i in range(uvBase.shape[0]):
        # temp1 = [x1,y1,1,0,0,0,-x1x2,-y1x2]
        temp1 = [uvBase[i,0],uvBase[i,1],uvBase[i,2],0,0,0,-uvBase[i,0]*uvTrans[i,0],-uvBase[i,1]*uvTrans[i,0]]
        # temp2 = [0,0,0,x1,y1,1,-x1y2,-y1y2]
        temp2 = [0,0,0,uvBase[i,0],uvBase[i,1],uvBase[i,2],-uvBase[i,0]*uvTrans[i,1],-uvBase[i,1]*uvTrans[i,1]]
        A.append(temp1)
        A.append(temp2)
        T.append(uvTrans[i,0])
        T.append(uvTrans[i,1])

    # A * H = T
    # 这里 A 的shape是 2n * 8 的，为了能够求逆，取四个点,默认H的第九个自由度为1
    A = np.array(A)
    T = np.array(T)
    H_ = np.linalg.solve(A,T)
    H = []
    for i in range(H_.shape[0]):
        H.append([H_[i]])
    H.append([1])
    H = np.array(H)

    return H

'''
主函数
'''
if __name__ == '__main__':
    # 取点
    pos_left,pos_right = getpoints(img_left,img_right,4)
    montage(img_left,img_right)
    # 转换成齐次坐标
    uvBase = homogen(pos_left)
    uvTrans = homogen(pos_right)
    # 计算H矩阵
    H = DIL(uvBase,uvTrans)
    print(H)