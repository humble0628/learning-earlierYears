'''
参数整定
'''
#=================================
XYZ = [
    [0,0.07,0.07],
    [0,0.21,0.21],
    [0.7,0.7,0],
    [0.21,0.21,0],
    [0.07,0,0.07],
    [0.21,0,0.21]
]  # 三维坐标的标注,单位是米
uv = []
im = 'pic4.jpg'
#=================================

'''
模块导入
'''
import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
import matplotlib.pyplot as plt
'''
================================================
代码总体流程：
1.图片取点，获取图片坐标系下的二维uv坐标，同时手动标注其世界坐标系下的三维XYZ坐标
2.1 使用DLT算法实现投影矩阵的计算
2.2 使用神经网络迭代获得关系，当然此方案需要的点数量更多
3.展示图，包括矩阵
================================================
'''

'''
相机标定：
1.世界坐标系到相机坐标系，得到相机外参(R,T矩阵)，确定相机在现实世界的位置和朝向，是三维到三维的转换；
2.相机坐标系到像素坐标系，得到相机内参K(焦距和主点位置)，是三维到二维的转换；
3.最后得到投影矩阵 P=K [ R | t ] 是一个3×4矩阵，K是内参，[ R | T ]是外参。
4.双目标定还需要得到双目之间的平移旋转矩阵，RT矩阵。
'''

# 功能函数1：将坐标对转化成齐次坐标
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

# 功能函数2：求矩阵的转置
def tranform(matrix):
    temp = []
    out = []
    for j in range(matrix.shape[1]):
        for i in range(matrix.shape[0]):
            temp.append(matrix[i][j])
        out.append(temp)
        temp = []

    return np.array(out)

'''
DLT方案
'''
class CamCalibrate(object):

    def __init__(self,im,XYZ,uv):
        self.im = im
        self.XYZ = XYZ
        self.uv = uv

    def Getpoints(self,num):
        img = Image.open(self.im)
        img = np.array(img)
        plt.imshow(img)
        self.uv = plt.ginput(num)
        self.uv = np.array(self.uv)

    def draw(self):
        in_img = cv2.imread(im)
        in_img = cv2.cvtColor(in_img,code=cv2.COLOR_BGR2RGB)
        for i in range(self.uv.shape[0]):
            cv2.circle(in_img,(int(self.uv[i,0]),int(self.uv[i,1])),5,(255,0,0),-1)
            out_img = Image.fromarray(in_img)
            out_img.save('out_pic4.jpg')


    # 此时的已知量有二维点坐标对，三维点坐标对
    def DLT(self):
        # 第一个操作是将坐标对变成齐次坐标形式
        self.XYZ = np.array(self.XYZ)
        self.uv = np.array(self.uv)
        self.XYZ = homogen(self.XYZ)
        self.uv = homogen(self.uv)

        print('----------------------DLT calibration begins------------------------')
        print('\n')
        # 第二个操作是生成 BL = C 中的B矩阵
        B = []
        out = []
        for i in range(self.XYZ.shape[0]):
            # temp1 = [X,Y,Z,1,0,0,0,0,-uX,-uY,-uZ,0]
            temp1 = [self.XYZ[i,0],self.XYZ[i,1],self.XYZ[i,2],self.XYZ[i,3],0,0,0,0,-self.uv[i,0]*self.XYZ[i,0],-self.uv[i,0]*self.XYZ[i,1],-self.uv[i,0]*self.XYZ[i,2],0]
            # temp2 = [0,0,0,0,X,Y,Z,1,-vX,-vY,-vZ,0]
            temp2 = [0,0,0,0,self.XYZ[i,0],self.XYZ[i,1],self.XYZ[i,2],self.XYZ[i,3],-self.uv[i,1]*self.XYZ[i,0],-self.uv[i,1]*self.XYZ[i,1],-self.uv[i,1]*self.XYZ[i,2],0]
            B.append(temp1)
            B.append(temp2)
            out.append(self.uv[i,0])
            out.append(self.uv[i,1])
        B[11][11] = 1
        # 第三个操作是求 L 的值 ,这里默认第12个参数为 1 ，求得的L矩阵为 11x1
        B = np.array(B)
        out = np.array(out)
        L_ = np.linalg.solve(B,out)

        l12 = 0
        for i in range(L_.shape[0]-1):
            l12 += -B[11,i] * L_[i] + out[11]
        L = L_ / l12

        # 由于求得的L是 12x1 的形状，还要转成 3x4
        C = np.zeros((3,4))
        for i in range(C.shape[0]):
            for j in range(C.shape[1]):
                C[i,j] = L[C.shape[1]*i + j]

        print('相机标定矩阵为：\n',C)
        # 第四个操作是将 C 矩阵分解 为 K [R | T],取第一对对应点来计算
        # 首先，相机内参数 [ 1/dx 0 u0 ]  [ f 0 0 0 ]
        #               [ 0 1/dy v0 ]  [ 0 f 0 0 ]
        #               [ 0  0  1 ]    [ 0 0 1 0 ]
        # fu = f/dx  , fv = f/dy
        u0 = C[0,0]*C[2,0] + C[0,1]*C[2,1] + C[0,2]*C[2,2]
        v0 = C[1,0]*C[2,0] + C[1,1]*C[2,1] + C[1,2]*C[2,2]
        fu = pow(abs(C[0,0]**2 + C[0,1]**2 + C[0,2]**2 - u0**2),0.5)
        fv = pow(abs(C[1,0]**2 + C[1,1]**2 + C[1,2]**2 - v0**2),0.5)

        print('相机的内参fu，fv，u0，v0分别是：%f,%f,%f,%f',(fu,fv,u0,v0))

        K_ = [[fu,0,u0,0],
             [0,fv,v0,0],
             [0,0, 1, 0]]

        print('K矩阵为：\n',np.array(K_))

        # 这里为了使用numpy，需要将矩阵变成方阵
        K_.append([0,0,0,1])
        C_ = []
        temp3 = []
        for i in range(C.shape[0]):
            for j in range(C.shape[1]):
                temp3.append(C[i,j])
            C_.append(temp3)
            temp3 = []
        C_.append([0,0,0,1])
        # 得到最终的方阵
        K_ = np.array(K_)
        C_ = np.array(C_)

        RT = np.linalg.solve(K_,C_)
        R = RT[:3,:3]
        T = RT[:3,3:]

        print('R矩阵为：\n',R)
        print('T矩阵为：\n',T)
        print('\n')
        print('-----------------------finish calibrating camera-------------------------')

'''
神经网络方案
'''
class NNplan(object):

    def __init__(self,im,XYZ_num,uv_num):
        self.im = im
        self.XYZ_num = XYZ_num
        self.uv_num = uv_num

    def Getpoints(self):
        img = Image.open(self.im)
        img = np.array(img)
        plt.imshow(img)
        pos2 = plt.ginput(self.uv_num)

        return pos2

    def nn(self,pos2,pos3):
        x_train = np.array(pos2)
        y_train = np.array(pos3)
        weights = tf.Variable(tf.zeros([3,4]))

        y_pred = np.matmul(weights,x_train)

        loss = tf.reduce_mean(tf.square(y_pred-y_train))
        optimizer = tf.train.GradientDescentOptimizer(0.5)
        train = optimizer.minimize(loss)

        sess = tf.Session()
        sess.run(tf.initialize_all_variables())
        for i in range(51):
            sess.run(train)
            if i % 10 == 0:
                print(i,sess.run(weights))

        return sess.run(weights)

    def draw(self):
        pass

'''
主函数
'''
if __name__ == "__main__":
    C = CamCalibrate(im,XYZ,uv)
    C.Getpoints(6)
    C.draw()
    C.DLT()

