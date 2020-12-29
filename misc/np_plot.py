import matplotlib.pyplot as plt
import numpy as np
from test2 import *

np_data = np.load('my_numpy.npz')['tracking']
colors = ['y','m','c','r','g','b','w','k']
bot_group = list(zip(*np_data[:80]))

for i in range(n_bots):
    plt.plot(bot_group[i], color=colors[i], label = "group {}".format(i))

plt.xlabel('Number of iterations')
plt.ylabel('Number of grid tiles for each robot')
plt.legend()
plt.show()


