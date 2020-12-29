import pyqtgraph.opengl as opengl
from pyqtgraph import glColor
from pyqtgraph.Qt import QtCore,QtGui
import sys
import numpy as np
import time
import random
import argparse
import math
import cv2
import matplotlib.pyplot as plt

nx, ny = 15, 15
n_bots = 3

class Track_Grid:
    def __init__(self):
        self.A = np.full(shape = (nx, ny), fill_value=-1)
        self.init_robot_pos =  [[4,5], [13, 12], [8, 3]] #[[random.randint(0,nx-1), random.randint(0,ny-1)] for i in range(n_bots)]
        self.bot_vals = list(range(n_bots))
        self.E = np.zeros((n_bots, nx, ny))
        self.K = [0]*n_bots
        self.M = [500]*n_bots
        self.fair_share = nx*ny/n_bots
        self.c = 0.01
        for bot in range(n_bots):
            for x in range(nx):
                for y in range(ny):
                    dist = np.linalg.norm(np.array(self.init_robot_pos[bot]) - np.array((x,y)))
                    self.E[bot,x,y] = dist
        self.track_K = []
        '''self.obstacle = -1
        self.blocks = self.binary_map_to_grid()'''

        for n, i in enumerate(self.init_robot_pos):
            self.A[i[0], i[1]] = self.bot_vals[n]
        '''for j in self.blocks:
            self.A[j[0],j[1]] =self.obstacle'''
    
    def binary_map_to_grid(self):
        image = cv2.imread("bn_map.jpeg",0)
        image = cv2.resize(image, (nx,ny))
        blocks=[]
        for x in range(nx):
            for y in range(ny):
                if image[x,y]==0:
                    blocks.append([x,y])
        return blocks

    def nearnest_circle(self, bot, n, val):
        for x in range(nx):
            for y in range(ny):
                dist = np.linalg.norm(np.array(bot) - np.array((x,y)))
                if dist<=n:
                    if self.A[x,y]>5 or self.A[x,y]<0:
                        pass
                    else:
                        self.A[x,y] = val
    def Update_M(self):    
        for i in range(n_bots):
            self.M[i] = self.M[i] + self.c*(self.K[i] - self.fair_share)

class GuiGrid(Track_Grid):  
    def __init__(self):
        super().__init__()
        self.app=QtGui.QApplication(sys.argv)
        self.window = opengl.GLViewWidget()
        self.window.setGeometry(0,410,600,600)
        self.window.setCameraPosition(distance=19,azimuth=270)
        grid=opengl.GLGridItem()
        grid.setSize(x=nx,y=ny)
        self.window.addItem(grid)
        self.black = (0., 0., 0., 1.)
        self.red = (1., 0., 0., 1.)
        self.green = (0., 1., 0., 1.)
        self.blue = (0., 0., 1., 1.)
        self.white = (1., 1., 1., 1.)
        self.mapped_grid = self.get_mapping()
        self.counter = 0
        #y_axis=opengl.GLGridItem()
        #y_axis.rotate(90,0,1,0)
        self.window.show()
    
    def get_mapping(self):
        mapped_grid = np.empty((nx,ny), dtype=object)
        for x in range(nx):
            for y in range(ny):
                size = np.empty((nx,ny,3))
                pos = np.empty((nx,ny,3))
                size[...,:] = [1,1,0]
                pos[...,:] = [x-nx/2, y-ny/2, 0]
                area = opengl.GLBarGraphItem(pos, size)
                area.setColor(self.black)
                self.window.addItem(area)
                mapped_grid[x,y] = area
        return mapped_grid

    def update(self):

        for x in range(nx):
            for y in range(ny):
                if self.A[x,y]==-1:
                    self.mapped_grid[x, y].setColor(self.black)
                elif self.A[x,y]==self.bot_vals[0]:
                    self.mapped_grid[x, y].setColor(self.green)
                elif self.A[x,y]==self.bot_vals[1]:
                    self.mapped_grid[x, y].setColor(self.red)                    
                elif self.A[x,y]==self.bot_vals[2]:
                    self.mapped_grid[x, y].setColor(self.blue)
                '''elif self.A[x,y]==self.obstacle:
                    self.mapped_grid[x, y].setColor(self.black)'''

        
        if self.counter%10==0:
            '''for k in range(3):
                self.nearnest_circle(self.init_random_pos[k], self.counter//10, self.bot_vals[k])'''
            '''for x in range(nx):
                for y in range(ny):
                    dmin = math.hypot(nx-1, ny-1)
                    j = -1
                    for kr, r in enumerate(self.init_random_pos):
                        d = math.hypot(r[0]-x, r[1]-y)
                        if d < dmin:
                            dmin = d
                            j = kr
                    if self.A[x,y]==-1:
                        pass
                    else:
                        self.A[x,y] = self.bot_vals[j]'''

            self.A = np.argmin(self.E, axis=0)

            for n in range(n_bots):
                self.K[n] = np.count_nonzero(self.A == self.bot_vals[n])
            
            self.Update_M()

            for i in range(n_bots):
                self.E[i] = self.M[i] * self.E[i]
            
            self.track_K.append(self.K[:])
            np.savez("my_numpy", tracking = np.array(self.track_K))

        self.counter+=1


    def start(self):
            if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
                QtGui.QApplication.instance().exec_()

    def animation(self,frametime=10):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(frametime)

        self.start()
    
if __name__ == "__main__":
    g=GuiGrid()
    g.animation()




