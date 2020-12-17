import pandas as pd
import numpy as np
import seaborn as sns
import tensorflow as tf
import matplotlib.pyplot as plt

'''
数据导入
'''
df1 = pd.read_csv('data1.csv',names=['square','bedrooms','price'])
df1.head()

'''
绘制散点图
'''
sns.set(context="notebook",style="whitegrid",palette="dark")
sns.lmplot('square','price',df1,height=6,fit_reg=False)
# plt.show()

'''
数据处理
'''
def normalize_feature(df):
    return df.apply(lambda column:(column - column.mean()) / column.std())

df = normalize_feature(df1)
# 绘制一个全为1的一列数，行数与数据行数相同
ones = pd.DataFrame({'ones':np.ones(len(df))})
# 把全为1的列向量与原数据表格合并
df = pd.concat([ones,df],axis=1)
# 用切片操作取x，y数据
X_data = np.array(df[df.columns[0:3]])
Y_data = np.array([df[df.columns[-1]]]).reshape(len(df),1)
print(X_data.shape)
print(Y_data.shape)

'''
模型结构
'''
alpha = 0.01 # 学习率
epoch = 500
with tf.name_scope('input'):
    X = tf.placeholder(tf.float32,X_data.shape) # [47,3]
    Y = tf.placeholder(tf.float32,Y_data.shape) # [47,1]

with tf.name_scope('hypothesis'):
    # 权重变量，形状为[3,1]
    W = tf.get_variable("weights",(X_data.shape[1],1),initializer=tf.constant_initializer())
    # 假设函数h(x) = w0*x0+w1*x1+w2*x2
    # 推理值y_pred，形状[47,1]
    y_pred = tf.matmul(X,W)

with tf.name_scope('loss'):
    # 损失函数采用最小二乘法
    # matmul(a,b,transpose_a=True)表示：矩阵a的转置乘b
    loss_op = 1 / (2 * len(X_data)) * tf.matmul((y_pred - Y),(y_pred - Y),transpose_a=True)

with tf.name_scope('train'):
    opt = tf.train.GradientDescentOptimizer(learning_rate=alpha)
    train_op = opt.minimize(loss_op)

'''
创建会话(运行环境)
'''
with tf.Session() as sess:
    # 初始化全局变量
    sess.run(tf.global_variables_initializer())
    # 创建FileWriter实例，并传入当前会话加载的数据流图
    # ./ 表示在当前目录下新建一个summary，并将数据流图命名为linear-regression-1，存放在summary下边
    writer = tf.summary.FileWriter('./summary/linear-regression-1',sess.graph)
    # 开始训练模型
    # 因为训练集较小，所以采用批梯度下降优化算法，每次都使用全量数据训练
    for i in range(1,epoch+1):
        sess.run(train_op,feed_dict={X:X_data,Y:Y_data})
        if i % 10 == 0:
            loss,w = sess.run([loss_op,W],feed_dict={X:X_data,Y:Y_data})
            log_str = "Epoch %d \t Loss=%.4g \t Model:y = %.4gx1 + %.4gx2 + %.4g"
            print(log_str % (i,loss,w[1],w[2],w[0]))

# 关闭FileWriter的输出流
writer.close()