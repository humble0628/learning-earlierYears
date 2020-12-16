import tensorflow as tf

state = tf.Variable(0,name='counter')
#定义state变量时，需要用到Variable变量
#其中0是初始值，名字是counter

one = tf.constant(1)

new_value = tf.add(state,one)
update = tf.assign(state,new_value)

init = tf.global_variables_initializer()#初始化Variable，必须要加

with tf.Session() as sess:
    sess.run(init)#运行初始化这一操作
    for _ in range(3):
       sess.run(update)
       print(sess.run(state))

