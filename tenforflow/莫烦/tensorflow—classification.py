import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data##数据集
#number 1 to 10
mnist=input_data.read_data_sets("D:/neural network/MNIST_data/",one_hot=True)#下载数据包
### mnist 包括train数据和test数据
def add_layer(inputs,in_size,out_size,activation_function=None):
    Weights = tf.Variable(tf.random_normal([in_size,out_size]))
    biases = tf.Variable(tf.zeros([1,out_size]) + 0.1)  ###biases初始值一般不设为0
    Wx_plus_b = tf.matmul(inputs,Weights) + biases  ###matmul是矩阵乘法
    if activation_function is None:
        outputs = Wx_plus_b
    else:
        outputs = activation_function(Wx_plus_b)
    return outputs

def compute_accuracy(v_xs,v_ys):
    global prediction
    y_pre = sess.run(prediction,feed_dict={xs:v_xs})##把xs代入，生成预测值
    correct_prediction = tf.equal(tf.argmax(y_pre,1),tf.argmax(v_ys,1))#对比xs值和真实值的差别，=1正确
    accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))#查看有多少值正确
    result = sess.run(accuracy,feed_dict={xs:v_xs,ys:v_ys})
    return result

# define placeholder fo inputs to network
xs = tf.placeholder(tf.float32,[None,784])
ys = tf.placeholder(tf.float32,[None,10])

# add output layer
prediction = add_layer(xs,784,10,activation_function=tf.nn.softmax)
###这一步的激励函数和损失函数都是适用于classification的
# the error between prediction and real data
cross_entropy = tf.reduce_mean(-tf.reduce_sum(ys*tf.log(prediction),reduction_indices=[1]))

train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)
sess = tf.Session()
# important step
sess.run(tf.initialize_all_variables())

for i in range(1000):
    batch_xs,batch_ys = mnist.train.next_batch(100)###minibatch_size,每次只学习100个数据，提高效率
    sess.run(train_step,feed_dict={xs:batch_xs,ys:batch_ys})
    if i % 50 ==0:
        print(compute_accuracy(mnist.test.images,mnist.test.labels))

