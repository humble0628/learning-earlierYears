import tensorflow as tf
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
# load data
digits = load_digits()#0-9的图片数据data,类似于minist，y等于多少就在该位置标上1
X = digits.data
y = digits.target
y = LabelBinarizer().fit_transform(y)
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.3)

def add_layer(inputs,in_size,out_size,n_layer,activation_function=None):
    layer_name = 'layer%s' % n_layer
    Weights = tf.Variable(tf.random_normal([in_size,out_size]))
    biases = tf.Variable(tf.zeros([1,out_size]) + 0.1)  ###biases初始值一般不设为0
    Wx_plus_b = tf.matmul(inputs,Weights) + biases  ###matmul是矩阵乘法
    if activation_function is None:
        outputs = Wx_plus_b
    else:
        outputs = activation_function(Wx_plus_b)
    tf.summary.histogram(layer_name + '/outputs', outputs)
    return outputs

# define placeholder for inputs to network

xs = tf.placeholder(tf.float32,[None,64])# 8×8
ys = tf.placeholder(tf.float32,[None,10])

# add output layer
l1 = add_layer(xs,64,100,'l1',activation_function=tf.nn.tanh)#隐藏层
prediction = add_layer(l1,100,10,'l2',activation_function=tf.nn.softmax)#输出层

# the loss between prediction and real data
cross_entropy = tf.reduce_mean(-tf.reduce_sum(ys*tf.log(prediction),reduction_indices=[1]))
tf.summary.scalar('loss',cross_entropy)
train_step = tf.train.GradientDescentOptimizer(0.6).minimize(cross_entropy)
sess = tf.Session()
merged = tf.summary.merge_all()
# summary writer goes in here
train_writer = tf.summary.FileWriter("logs/train",sess.graph)
test_writer = tf.summary.FileWriter("logs/test",sess.graph)

sess.run(tf.initialize_all_variables())

for i in range(500):
    sess.run(train_step,feed_dict={xs:X_train,ys:y_train})
    if i%50 == 0:
        # record loss
        train_result = sess.run(merged,feed_dict={xs:X_train,ys:y_train})
        test_result = sess.run(merged,feed_dict={xs:X_test,ys:y_test})
        train_writer.add_summary(train_result,i)
        test_writer.add_summary(test_result,i)

