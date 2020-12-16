import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

def add_layer(inputs,in_size,out_size,activation_function=None):
    Weights = tf.Variable(tf.random_normal([in_size,out_size]))
    biases = tf.Variable(tf.zeros([1,out_size]) + 0.1)  ###biases初始值一般不设为0
    Wx_plus_b = tf.matmul(inputs,Weights) + biases  ###matmul是矩阵乘法
    if activation_function is None:
        outputs = Wx_plus_b
    else:
        outputs = activation_function(Wx_plus_b)
    return outputs

x_data = np.linspace(-1,1,300)[:,np.newaxis]
noise = np.random.normal(0,0.05,x_data.shape)##这里的意思是在函数值上加一些干扰，干扰值的分布事方差0.05，均值为0
y_data = np.square(x_data) - 0.5 + noise


xs = tf.placeholder(tf.float32,[None,1])
ys = tf.placeholder(tf.float32,[None,1])
###设置隐藏层，10个神经元
l1 = add_layer(xs,1,10,activation_function=tf.nn.relu)##hidden layer
#隐藏层的输入值是x_data,输入大小是1，输出是10
prediction = add_layer(l1,10,1,activation_function=None)##output layer

loss = tf.reduce_mean(tf.reduce_sum(tf.square(ys - prediction),
                   reduction_indices=[1]))
####这步mean意思是求平均值，sum求和，reduction indices意思是把该值降到1维
train_step = tf.train.GradientDescentOptimizer(0.1).minimize(loss)
#训练的目的是把损失loss减小，学习率为0.1
init = tf.initialize_all_variables()
sess = tf.Session()
sess.run(init)

####可视化
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.scatter(x_data,y_data)
plt.ion()##让show连续
plt.show()
###training
for i in range(1000):
    ###这里用xs和ys是为了dropout
    sess.run(train_step,feed_dict={xs:x_data,ys:y_data})
    if i % 50==0:
        ###print(sess.run(loss,feed_dict={xs:x_data,ys:y_data}))
        try:
            ax.lines.remove(lines[0])
        except Exception:
            pass
        prediction_value = sess.run(prediction,feed_dict={xs:x_data})
        lines = ax.plot(x_data,prediction_value,'r-',lw=5)

        plt.pause(0.3)


