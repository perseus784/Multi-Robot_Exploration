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

nx, ny = 20, 20

class Track_Grid:
    def __init__(self):
        self.np_grid = np.zeros(shape = (nx,ny))
        self.init_random_pos = [[random.randint(0,nx-1), random.randint(0,ny-1)] for i in range(3)]
        self.bot_vals = [6,7,8]
        self.obstacle =-1
        self.blocks = self.binary_map_to_grid()

        for n, i in enumerate(self.init_random_pos):
            self.np_grid[i[0],i[1]] = self.bot_vals[n]
        for j in self.blocks:
            self.np_grid[j[0],j[1]] =self.obstacle
        self.binary_map_to_grid()
    
    def binary_map_to_grid(self):
        image = cv2.imread("binary_map.jpeg",0)
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
                    if self.np_grid[x,y]>5 or self.np_grid[x,y]<0:
                        pass
                    else:
                        self.np_grid[x,y] = val

class GuiGrid(Track_Grid):
    def __init__(self):
        super().__init__()
        self.app=QtGui.QApplication(sys.argv)
        self.window = opengl.GLViewWidget()
        self.window.setGeometry(0,410,600,600)
        self.window.setCameraPosition(distance=12,azimuth=270)
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
                if self.np_grid[x,y]==0:
                    self.mapped_grid[x, y].setColor(self.black)
                elif self.np_grid[x,y]==self.bot_vals[0]:
                    self.mapped_grid[x, y].setColor(self.green)
                elif self.np_grid[x,y]==self.bot_vals[1]:
                    self.mapped_grid[x, y].setColor(self.red)                    
                elif self.np_grid[x,y]==self.bot_vals[2]:
                    self.mapped_grid[x, y].setColor(self.blue)
                elif self.np_grid[x,y]==self.obstacle:
                    self.mapped_grid[x, y].setColor(self.white)

        
        if self.counter%10==0:
            '''for k in range(3):
                self.nearnest_circle(self.init_random_pos[k], self.counter//10, self.bot_vals[k])'''
            for x in range(nx):
                for y in range(ny):
                    dmin = math.hypot(nx-1, ny-1)
                    j = -1
                    for kr, r in enumerate(self.init_random_pos):
                        d = math.hypot(r[0]-x, r[1]-y)
                        if d < dmin:
                            dmin = d
                            j = kr
                    if self.np_grid[x,y]==-1:
                        pass
                    else:
                        self.np_grid[x,y] = self.bot_vals[j]

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




