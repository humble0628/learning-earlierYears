'''
模块导入
'''
import os
import gym
import time
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from gym.envs.registration import register

'''
============================================================================
                                    思路
1.大环境：小车可移动范围是[-2.4,2.4],杆的最大偏离角是15°，如果不满足任意一个条件，则失败
2.创建智能体：包括小车和杆，信息有小车速度，小车位置，杆的角度，杆的角速度
3.创建Q表，一共有两列，第一列是state，第二列是action。我设置智能体的每一种信息都有六种 子状态
因此，总共的状态有6**4种，action只能左移和右移，因此Q表的size=(6**4,2)
4.决策过程：Q表首先初始化，每一个值都初始化为0-1的随机数，然后每一次移动都要根据公式对Q表进行
更新，有一定概率选择Q表中的大值，其余的概率为随机选择，目的是使尽可能多的值都能得到更新
5.环境刷新：首先初始化环境，初始化的状态是在6**4种状态中随机的，小车每走一步更新一次Q表，
刷新一帧环境，当触发失败条件后，重新初始化环境，如此迭代。
============================================================================
'''

'''
参数整定
'''
#===========================================
ENV = 'CartPole-v2'
NUM_DIGITIZED = 6
GAMMA = 0.99 #decrease rate
ETA = 0.5 #learning rate
MAX_STEPS = 2000 #steps for 1 episode
NUM_EPISODES = 3000 #number of episodes
#===========================================

'''
智能体
'''
class Agent:
    def __init__(self, num_states, num_actions):
        self.brain = Brain(num_states, num_actions)

    # update the Q function
    def update_Q_function(self, observation, action, reward, observation_next):
        self.brain.update_Q_table(
            observation, action, reward, observation_next)

    # get the action
    def get_action(self, observation, step):
        action = self.brain.decide_action(observation, step)
        return action

'''
决策过程
'''
class Brain:
    # do Q-learning

    def __init__(self, num_states, num_actions):
        self.num_actions = num_actions  # the number of CartPole actions

        # create the Q table, row is the discrete state(digitized state^number of variables), column is action(left, right)
        self.q_table = np.random.uniform(low=0, high=1, size=(
        NUM_DIGITIZED ** num_states, num_actions))  # uniform distributed sample with size

    def bins(self, clip_min, clip_max, num):
        # bin一般是升序或者降序序列，此函数去掉了首尾
        # convert continous value to discrete value
        return np.linspace(clip_min, clip_max, num + 1)[1: -1]  # num of bins needs num+1 value

    def digitize_state(self, observation):
        # get the discrete state in total 1296 states
        cart_pos, cart_v, pole_angle, pole_v = observation

        # 依据环境限制条件，创建智能体状态序列，共有6**4种状态
        digitized = [
            np.digitize(cart_pos, bins=self.bins(-2.4, 2.4, NUM_DIGITIZED)),
            np.digitize(cart_v, bins=self.bins(-3.0, 3.0, NUM_DIGITIZED)),
            np.digitize(pole_angle, bins=self.bins(-0.5, 0.5, NUM_DIGITIZED)),  # angle represent by radian
            np.digitize(pole_v, bins=self.bins(-2.0, 2.0, NUM_DIGITIZED))
        ]
        # 这里类似于 卡尔曼滤波
        return sum([x * (NUM_DIGITIZED ** i) for i, x in enumerate(digitized)])

    def update_Q_table(self, observation, action, reward, observation_next):
        # Q表的结构：state    action
        #            0      0    1
        #            1
        #            2
        #            3
        #            4
        # Q表的状态总数共有6**4个，代表了小车与杆子的全部状态，而可以采取的行动只有2种：小车左移和小车右移
        state = self.digitize_state(observation)
        state_next = self.digitize_state(observation_next)
        Max_Q_next = max(self.q_table[state_next][:])
        self.q_table[state, action] = self.q_table[state, action] + \
                                      ETA * (reward + GAMMA * Max_Q_next - self.q_table[state, action])

    def decide_action(self, observation, episode):
        # epsilon-greedy
        # 选择q表中正确值的概率会随着移动轮次的增加而增加
        state = self.digitize_state(observation)
        epsilon = 0.5 * (1 / (episode + 1))

        if epsilon <= np.random.uniform(0, 1):
            action = np.argmax(self.q_table[state][:])
        else:
            action = np.random.choice(self.num_actions)

        return action

'''
环境搭建
'''
class Environment:

    def __init__(self):
        self.env = gym.make(ENV)
        num_states = self.env.observation_space.shape[0]
        num_actions = self.env.action_space.n
        self.agent = Agent(num_states, num_actions)
        self.gif500 = 'gif500'
        self.gif1000 = 'gif1000'
        self.gif2000 = 'gif2000'

    def run(self):
        complete_episodes = 0

        for episode in range(NUM_EPISODES):
            observation = self.env.reset()

            for step in range(MAX_STEPS):

                self.frame = self.env.render(mode='rgb_array')
                action = self.agent.get_action(observation, episode)

                observation_next, _, done, _ = self.env.step(action)

                # 设置回馈更新方式
                if done:
                    if step < 195 * 10:
                        reward = -1
                        complete_episodes = 0
                    else:
                        reward = 1
                        complete_episodes += 1
                else:
                    reward = 0

                # Q表的权值更新
                self.agent.update_Q_function(observation, action, reward, observation_next)
                observation = observation_next

                # 图片保存，用于制作动态图
                # if episode >= 500 and episode < 520:
                #     save = Image.fromarray(self.frame)
                #     save.save('%s/%d.jpg' % (self.gif500,episode))
                #
                # if episode >= 1000 and episode < 1020:
                #     save = Image.fromarray(self.frame)
                #     save.save('%s/%d.jpg' % (self.gif1000,episode))
                #
                # if episode >= 2000 and episode < 2020:
                #     save = Image.fromarray(self.frame)
                #     save.save('%s/%d.jpg' % (self.gif2000,episode))

                if done:
                    print('{0} Episode: Finished after {1} time steps'.format(episode, step + 1))
                    break

    #def compose_gif(self):

'''
主程序
'''
if __name__ == "__main__":
    register(
        id = 'CartPole-v2',
        entry_point='gym.envs.classic_control:CartPoleEnv',
        max_episode_steps = 200 * 10,
        reward_threshold = 195 * 10,
    )
    env = Environment()
    env.run()