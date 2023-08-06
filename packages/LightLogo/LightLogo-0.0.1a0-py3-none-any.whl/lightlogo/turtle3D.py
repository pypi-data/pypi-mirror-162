# Copyright © 2022, Donghua Chen
# All Rights Reserved
# Software Name: LightLogo
# By: Donghua Chen (https://github.com/dhchenx)
# License: BSD-3 - https://github.com/dhchenx/LightLogo/blob/main/LICENSE

#                         BSD 3-Clause License
#
# Copyright (c) 2022, Donghua Chen
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy as np
import math

'''
    a turtle in a 3D world
'''
class turtle3D:

    turtle_counter = 0

    @staticmethod
    def turtle_id():
        turtle3D.turtle_counter = turtle3D.turtle_counter + 1
        return turtle3D.turtle_counter + 1

    def __init__(self,x=0,y=0,z=0,xyz=None,shape="*",size=1,color="blue",type="turtle",variables:dict=None):
        self.x=x
        self.y=y
        self.z=z
        self._id=turtle3D.turtle_id()

        if xyz!=None:
            self.x=xyz[0]
            self.y=xyz[1]
            self.z=xyz[2]

        self.old_xyz=[self.x,self.y,self.z]
        self.old_color=color
        self.old_shape=shape
        self.old_size=size

        self._fullcircle=360
        self._angleOrient = 1 #
        self.x_rotate = 0
        self.y_rotate=0
        self.z_rotate=0
        self.line_points=[]
        self.drawing=False
        self._shape=shape
        self._size=size
        self._color=color
        self.pen_dict= {
            "color" : 'blue', "marker" : '.', "linestyle": '-', "linewidth": 1, "markersize" :5
        }
        self.clicked_event=None
        self.pressed_event=None
        self.is_dead=False
        self.is_cleared=False
        self.visible=True
        self._pen_mode="line" # poly
        self._type=type
        self.variables={}
        if variables!=None:
            self.variables=variables

    # set variables
    def var(self,k):
        return self.variables[k]

    def setvar(self,k,v):
        self.variables[k]=v

    def vars(self):
        return self.variables

    def id(self):
        return str(self._id)

    def type(self,type=None):
        if type!=None:
            self._type=type
        return type

    def color(self,color=None):
        if color!=None:
            self._color=color
        return self._color

    def size(self,size=-1):
        if size!=-1:
            self._size=size
        return self._size

    def shape(self,shape=None):
        if shape!=None:
            self._shape=shape
        return self._shape


    def clicked(self,x,y,z):
        if self.clicked_event!=None:
            return self.clicked_event(self,x,y,z)

    def set_pressed(self,pressed_event):
        self.pressed_event=pressed_event

    def pressed(self,k):
        if self.pressed_event!=None:
            return self.pressed_event(self,k)

    def set_clicked(self,clicked_event):
        self.clicked_event=clicked_event

    def pen(self,pen_dict=None):
        if pen_dict!=None:
            for k in pen_dict:
                self.pen_dict[k]=pen_dict[k]

    def pendown(self):
        self.drawing=True
        self._pen_mode="line"

    def begin_poly(self):
        self.drawing=True
        self._pen_mode="poly"

    def penmode(self,mode=None):
        if mode!=None:
            self._pen_mode=mode
        return self._pen_mode

    def end_poly(self):
        self.drawing=False
        self._pen_mode="poly"

    def mark(self):
        self.line_points.append(self.pos())

    def penup(self):
        self._pen_mode="line"
        self.drawing=False

    def setx(self,x):
        self.x=x

    def sety(self,y):
        self.y=y

    def setz(self,z):
        self.z=z

    def setxyz(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z

    def print_cor(self):
        print(f"Turtle({self.x},{self.y},{self.z})")

    def x_rotate(self):
        return self.heading_

    def position(self):
        return [self.x,self.y,self.z]

    def setposition(self,x,y,z):
        self.setxyz(x,y,z)

    def setpos(self,x,y,z):
        self.setxyz(x, y, z)

    def pos(self):
        return self.position()

    def xcor(self):
        return self.x

    def ycor(self):
        return self.y

    def zcor(self):
        return self.z

    def distance(self,x1,y1,z1):
        return math.sqrt(math.pow((x1-self.xcor()),2)+math.pow((y1-self.ycor()),2)+math.pow((z1-self.zcor()),2))

    '''
    def forward(self,d):
        self.setx(self.x+d*math.acos(self.heading_*1.0/90))
        self.sety(self.y + d* math.asin(self.heading_ * 1.0 / 90))
    '''

    def Rx(self,theta):
        return np.matrix([[1, 0, 0],
                          [0, math.cos(theta), -math.sin(theta)],
                          [0, math.sin(theta), math.cos(theta)]])

    def Ry(self,theta):
        return np.matrix([[math.cos(theta), 0, math.sin(theta)],
                          [0, 1, 0],
                          [-math.sin(theta), 0, math.cos(theta)]])

    def Rz(self,theta):
        return np.matrix([[math.cos(theta), -math.sin(theta), 0],
                          [math.sin(theta), math.cos(theta), 0],
                          [0, 0, 1]])

    def getR(self,a, b, c):
        phi = a / 180 * math.pi
        theta = - b / 180 * math.pi
        psi = c / 180 * math.pi

        R = self.Rz(psi) * self.Ry(theta) * self.Rx(phi)
        # R = Rz(psi) * Ry(theta) * Rx(phi)
        # print(np.round(R, decimals=2))
        return R

    def forward(self,d):
        print(self.x_rotate,self.y_rotate,self.z_rotate)
        v1 = np.array([[d], [0], [0]])

        R = self.getR(self.x_rotate,self.y_rotate,self.z_rotate)

        v2 = R * v1

        v3 = v2 + np.array([[self.x], [self.y], [self.z]])
        v3=v3.tolist()
        # print("v3: ",v3)

        new_x=round(v3[0][0],4)
        new_y=round(v3[1][0],4)
        new_z=round(v3[2][0],4)
        print(new_x,",",new_y,",",new_z)
        self.setxyz(new_x,new_y,new_z)

    def backward(self,d):

        v1 = np.array([[-d], [0], [0]])

        R = self.getR(self.x_rotate,self.y_rotate,self.z_rotate)

        v2 = R * v1

        v3 = v2 + np.array([[self.x], [self.y], [self.z]])
        v3=v3.tolist()
        # print("v3: ",v3)

        new_x=round(v3[0][0],4)
        new_y=round(v3[1][0],4)
        new_z=round(v3[2][0],4)
        # print(new_x,",",new_y,",",new_z)
        self.setxyz(new_x,new_y,new_z)

    def forwardx(self,d):
        self.x=self.x+d

    def forwardy(self,d):
        self.y=self.y+d

    def forwardz(self,d):
        self.z=self.z+d

    def move(self,dx,dy,dz):
        self.x+=dx
        self.y+=dy
        self.z+=dz

    def moveto(self,cor):
        self.x=cor[0]
        self.y=cor[1]
        self.z=cor[2]

    def backwardx(self,d):
        self.x=self.x-d

    def backwardy(self,d):
        self.y=self.y-d

    def backwardz(self,d):
        self.z=self.z-d

    def fd(self,d):
        self.forward(d)

    def bk(self,d):
        self.backward(d)

    def rt(self,angle):
        self.right(angle)


    def lt(self,angle):
        self.left(angle)

    def left(self,angle):
        self.z_rotate=self.z_rotate+ angle
        self.z_rotate=self.z_rotate % self._fullcircle

    def right(self,angle):
        self.z_rotate=self.z_rotate - angle
        self.z_rotate=self.z_rotate % self._fullcircle

    def up(self,angle):
        self.y_rotate=self.y_rotate + angle
        self.y_rotate=self.y_rotate % self._fullcircle

    def down(self,angle):
        self.y_rotate=self.y_rotate - angle
        self.y_rotate=self.y_rotate % self._fullcircle

    def rollback(self,angle):
        self.x_rotate=self.x_rotate + angle
        self.x_rotate=self.x_rotate % self._fullcircle

    def rollforward(self,angle):
        self.x_rotate = self.x_rotate - angle
        self.x_rotate = self.x_rotate % self._fullcircle

    def setxrotate(self,xr):
        self.x_rotate=xr

    def setyrotate(self,yr):
        self.y_rotate=yr

    def setzrotate(self,zr):
        self.z_rotate=zr


    def goto(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z

    def home(self):
        self.setxyz(0,0,0)

    def towards(self,x,y,z):
        pass

    def show(self):
        self.visible=True

    def st(self):
        self.show()

    def ht(self):
        self.hide()

    def hide(self):
        self.visible=False

    def die(self):
        self.is_dead=True

    def isvisible(self):
        return self.visible

    def stamp(self):
        pass

    def clearstamp(self,stampid):
        pass

    def clearstamps(self):
        pass

    def clear(self):
        self.is_cleared=True

    def reset(self):
        self.setxyz(self.old_xyz[0],self.old_xyz[1],self.old_xyz[2])
        self.color(self.old_color)
        self.size(self.old_size)
        self.shape(self.old_shape)
        self.x_rotate = 0
        self.y_rotate = 0
        self.z_rotate = 0
        self.line_points = []
        self.drawing = False
        self.pen_dict = {
            "color": 'blue', "marker": '.', "linestyle": '-', "linewidth": 1, "markersize": 5
        }
        self.clicked_event = None
        self.is_dead = False
        self.visible = True
        self.clear()


    def width(self,width=None):
        if width!=None:
            self.pen_dict["linewidth"]=width
        return self.pen_dict["linewidth"]

    def pencolor(self,color=None):
        if color!=None:
            self.pen_dict["color"]=color
        return color

    def setheading(self,to_angle):
        '''
                 standard - mode:          logo-mode:
        -------------------|--------------------
           0 - east                0 - north
          90 - north              90 - east
         180 - west              180 - south
         270 - south             270 - west
        '''
        angle = to_angle + self.heading()
        self.heading_=angle
