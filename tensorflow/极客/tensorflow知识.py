import tensorflow as tf

'''
占位符操作placehoder:用来填充数据
x = placeholder(dtype,shape,name)
配合session执行操作
'''
x = tf.placeholder(tf.int16,shape=(),name="x")
y = tf.placeholder(tf.int16,shape=(),name="y")
add = tf.add(x,y)
with tf.Session() as sess:
    print(sess.run(add,feed_dict={x:2,y:3}))


'''
会话:Session
使用流程:1.创建会话 2.估算张量或执行操作 3.关闭会话
'''
sess = tf.Session(target='',graph=None,config=None)
sess.run()
sess.close()

