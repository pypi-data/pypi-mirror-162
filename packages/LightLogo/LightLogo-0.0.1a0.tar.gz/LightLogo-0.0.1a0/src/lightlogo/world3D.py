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

import random
from tkinter import Tk
from tkinter.simpledialog import askinteger, askfloat, askstring
from matplotlib import pyplot as plt
from matplotlib import animation
import sys
import numpy as np
from tkinter import messagebox
from lightlogo.turtle3D import *
from lightlogo.surface3D import *
from lightlogo.text3D import *

'''
    a 3D world filling with various agents, surfaces and objects. 
'''

class world3D:

    def __init__(self,x_range, y_range, z_range,title=""):
        # world dimensions
        self.x_range=x_range
        self.y_range=y_range
        self.z_range=z_range
        # a list of turtles
        self.list_turtles=[]
        self.list_surfaces=[]
        self.list_texts=[]
        # inner functions
        self.setup=None
        self.go=None
        # determine if the simulation is started
        self.is_start = False
        # store plot objects in the 3d world
        self.lines_ax= {}
        self.points_ax={}
        self.poly_ax={}
        self.surfaces_ax={}
        self.texts_ax={}
        # status of steps
        self.is_clicked=False
        self.is_pressed=False
        self.is_deleting=False
        # 3D world title
        self.title=title
        # available color value for random_color()
        self.colors = ["red", "orange", "yellow", "green", "blue", "violet"]
        # store the original x,y,z for reset()
        self.old_x_range=x_range
        self.old_y_range=y_range
        self.old_z_range=z_range
        # store the boolean value of exit condition
        self.should_exit_on_click=False
        self.should_exit_on_press = False
        self._last_input_value=""

    def create(self,x_label="X",y_label="Y",z_label="Z",proj_type="persp",style="seaborn-ticks",show_axes=True,show_xaxis=False,show_yaxis=False,show_grid=False,
               background_color=None,background_color_3d=None,
               # figure_width=4,figure_height=4,dpi=300
               ):
        # style options
        # ['Solarize_Light2', '_classic_test_patch', '_mpl-gallery', '_mpl-gallery-nogrid', 'bmh', 'classic',
        # 'dark_background', 'fast', 'fivethirtyeight', 'ggplot', 'grayscale', 'seaborn', 'seaborn-bright',
        # 'seaborn-colorblind', 'seaborn-dark', 'seaborn-dark-palette', 'seaborn-darkgrid', 'seaborn-deep',
        # 'seaborn-muted', 'seaborn-notebook', 'seaborn-paper', 'seaborn-pastel', 'seaborn-poster',
        # 'seaborn-talk', 'seaborn-ticks', 'seaborn-white', 'seaborn-whitegrid', 'tableau-colorblind10']
        # plt.style.use(style)
        with plt.style.context(style):

            self.fig = plt.figure()
            #self.fig.set_figwidth(figure_width)
            #self.fig.set_figheight(figure_height)
            #self.fig.set_dpi(dpi)
            self.ax = plt.axes(projection="3d")
            self.ax.set_proj_type(proj_type)

            self.ax.set_title(self.title)

            # Labelling X-Axis
            self.ax.set_xlabel(x_label)

            # Labelling Y-Axis
            self.ax.set_ylabel(y_label)

            # Labelling Z-Axis
            self.ax.set_zlabel(z_label)

            self.fig.canvas.mpl_connect('key_press_event', self.on_press)
            self.fig.canvas.mpl_connect('button_press_event', self.on_click)

            self.ax.set_xlim(self.x_range)
            self.ax.set_ylim(self.y_range)
            self.ax.set_zlim3d(bottom=self.z_range[0],top=self.z_range[1])

            self.ax.axis(show_axes)

            # self.ax.set_axis_on()

            self.ax.get_xaxis().set_visible(show_xaxis)
            self.ax.get_yaxis().set_visible(show_yaxis)

            self.ax.grid(show_grid)
            if background_color_3d!=None:
                self.ax.set_facecolor(background_color_3d)
            if background_color!=None:
                self.fig.set_facecolor(background_color)

        return self.ax

    def surfaces(self,surfaces=None):
        if surfaces!=None:
            self.list_surfaces=surfaces
        return self.list_surfaces

    def surface_at(self,idx):
        return self.list_surfaces[idx]

    def random_xcor(self):
        return random.randint(self.x_range[0],self.x_range[1])

    def random_ycor(self):
        return random.randint(self.y_range[0],self.y_range[1])

    def random_zcor(self):
        return random.randint(self.z_range[0],self.z_range[1])

    def random_cor(self):
        return [self.random_xcor(),self.random_ycor(),self.random_zcor()]

    def on_press(self,event):

        if self.should_exit_on_press:
            self.bye()

        self.is_pressed = True
        # print(f"Pressed {event.key}")
        k=event.key
        for idx in range(len(self.list_turtles)):
            turtle = self.list_turtles[idx]
            if turtle.pressed_event != None:
                self.list_turtles[idx]=turtle.pressed_event(turtle,k)
        self.is_pressed = False

    def oneOf(self):
        if len(self.list_turtles)==0:
            return -1,None
        if len(self.list_turtles)==1:
            return 0,self.list_turtles[0]
        tid= random.randint(0,len(self.list_turtles)-1)
        return tid,self.list_turtles[tid]

    def nOf(self,N):
        randomlist = random.sample(range(0, len(self.list_turtles)), N)
        list_new_turtles=[]
        for idx in randomlist:
            list_new_turtles.append(self.list_turtles[idx]-1)
        return randomlist,list_new_turtles

    def random_color(self):
        tid = random.randint(0, len(self.colors) - 1)
        return self.colors[tid]

    def update(self,turtles):
        if type(turtles)!=list:
            turtles=[turtles]
        if len(turtles)==0:
            return
        if str(type(turtles[0]))=="turtle3D":
            for turtle in turtles:
                for idx,turtle0 in enumerate(self.list_turtles):
                    if turtle.id()==turtle0.id():
                        self.list_turtles[idx]=turtle
                        break
        if str(type(turtles[0]))=="surface3D":
            for turtle in turtles:
                for idx,turtle0 in enumerate(self.list_surfaces):
                    if turtle.id()==turtle0.id():
                        self.list_surfaces[idx]=turtle
                        break

    def on_click(self,event):
        '''
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))
        '''

        if self.should_exit_on_click:
            self.bye()

        self.is_clicked=True
        # xyz=self.getxyz(event)
        try:
            x,y,z=self.get_xyz_mouse_click(event,self.ax)
            print(f"Clicked ({round(x,4)},{round(y,4)},{round(z,4)})")
            for idx in range(len(self.list_turtles)):
                turtle=self.list_turtles[idx]
                if turtle.clicked_event!=None:
                    self.list_turtles[idx]=turtle.clicked_event(turtle,x,y,z)
            self.is_clicked=False
        except Exception as err:
            pass



    def init(self):

        if self.setup!=None:
            self.setup(self)

        if len(self.list_turtles)==0:
            return

        '''
        list_x=[]
        list_y=[]
        list_z=[]
        list_shape=[]
        for idx,turtle in enumerate(self.list_turtles):
            list_x.append(turtle.xcor())
            list_y.append(turtle.ycor())
            list_z.append(turtle.zcor())
            list_shape.append(turtle.shape())
            ax_point, = self.ax.plot([turtle.xcor()],[turtle.ycor()], [turtle.zcor()], turtle.shape(),color=turtle.color(),markersize=turtle.size())
            self.points_ax[str(idx)]=ax_point

        #self.init_x = np.array(list_x)
        #self.init_y = np.array(list_y)
        #self.init_z = np.array(list_z)
        #self.points, = self.ax.plot(self.init_x, self.init_y, self.init_z, list_shape)
        '''
        self.txt = self.fig.suptitle('')

    def _vec_pad_ones(seflf,xs, ys, zs):
        return np.array([xs, ys, zs, np.ones_like(xs)])

    def inv_transform(self,xs, ys, zs, M):
        iM = np.linalg.inv(M)
        vec = self._vec_pad_ones(xs, ys, zs)
        vecr = np.dot(iM, vec)
        try:
            vecr = vecr / vecr[3]
        except OverflowError:
            pass
        return vecr[0], vecr[1], vecr[2]

    def _line2d_seg_dist(self,p1, p2, p0):
        """distance(s) from line defined by p1 - p2 to point(s) p0

        p0[0] = x(s)
        p0[1] = y(s)

        intersection point p = p1 + u*(p2-p1)
        and intersection point lies within segment if u is between 0 and 1
        """

        x21 = p2[0] - p1[0]
        y21 = p2[1] - p1[1]
        x01 = np.asarray(p0[0]) - p1[0]
        y01 = np.asarray(p0[1]) - p1[1]

        u = (x01 * x21 + y01 * y21) / (x21 ** 2 + y21 ** 2)
        u = np.clip(u, 0, 1)
        d = np.hypot(x01 - u * x21, y01 - u * y21)

        return d

    def get_xyz_mouse_click(self,event, ax):
        """
        Get coordinates clicked by user
        """
        if ax.M is None:
            return {}

        xd, yd = event.xdata, event.ydata
        p = (xd, yd)
        edges = ax.tunit_edges()
        ldists = [(self._line2d_seg_dist(p0, p1, p), i) for \
                  i, (p0, p1) in enumerate(edges)]
        ldists.sort()

        # nearest edge
        edgei = ldists[0][1]

        p0, p1 = edges[edgei]

        # scale the z value to match
        x0, y0, z0 = p0
        x1, y1, z1 = p1
        d0 = np.hypot(x0 - xd, y0 - yd)
        d1 = np.hypot(x1 - xd, y1 - yd)
        dt = d0 + d1
        z = d1 / dt * z0 + d0 / dt * z1

        x, y, z = self.inv_transform(xd, yd, z, ax.M)
        return x, y, z

    def update_worlds(self,num,points_ax,lines_ax):

        if self.is_clicked:
            print("doing clicked event, ignore this frame!")
            return self.points_ax, self.lines_ax

        if self.is_deleting:
            print("doing deleting event, ignore this frame!")
            return self.points_ax, self.lines_ax

        if not self.is_start:
            self.is_start=True
            return self.points_ax,self.lines_ax

        self.txt.set_text('Frame = {:d}'.format(num))  # for debug purposes

        # calculate the new sets of coordinates here. The resulting arrays should have the same shape
        if self.go!=None:
            self.go(num,self)

        # die
        # self.is_deleting=True
        print("points_ax: ",len(self.points_ax))
        list_new_turtles=[]
        for idx in range(len(self.list_turtles)):
            turtle_id=str(self.list_turtles[idx].id())
            if not self.list_turtles[idx].is_dead:
                list_new_turtles.append(self.list_turtles[idx])
            else:
                if str(turtle_id) in self.points_ax.keys():
                    self.points_ax.pop(turtle_id).remove()
                if str(turtle_id) in self.lines_ax.keys():
                    self.lines_ax.pop(turtle_id).remove()

        self.list_turtles=list_new_turtles

        # self.is_deleting=False

        # turtle agents create or update
        for turtle in self.list_turtles:
            idx=turtle.id()
            ax_point=None
            if str(idx) in self.points_ax.keys():
                ax_point=self.points_ax[str(idx)]
            else:
                ax_point, =  self.ax.plot([turtle.xcor()],[turtle.ycor()], [turtle.zcor()], marker= turtle.shape(), color=turtle.color(),markersize=turtle.size())
                self.points_ax[str(idx)]=ax_point
            ax_point.set_data([turtle.xcor()], [turtle.ycor()])
            # print(new_z)
            ax_point.set_3d_properties([turtle.zcor()], 'z')
            ax_point.set_markersize(turtle.size())
            ax_point.set_color(turtle.color())
            ax_point.set_marker(turtle.shape())

        # turtle's lines
        # clear lines
        for idx in range(len(self.list_turtles)):
            turtle=self.list_turtles[idx]
            # print("turtle drawing: ",turtle.drawing)
            if turtle.is_cleared == True:
                # print("marking")
                turtle.line_points=[]
                if turtle.id() in self.lines_ax.keys():
                    self.lines_ax.pop(turtle.id()).remove()
                turtle.is_cleared=False
            self.list_turtles[idx]=turtle

        # mark turtle line points
        for idx in range(len(self.list_turtles)):
            turtle=self.list_turtles[idx]
            # print("turtle drawing: ",turtle.drawing)
            if turtle.drawing == True:
                # print("marking")
                turtle.mark()
            self.list_turtles[idx]=turtle

        # create lines of each turtle
        for turtle in self.list_turtles:
            idx=turtle.id()
            list_line_x = []
            list_line_y = []
            list_line_z=[]
            # print("len of points: ",len(turtle.line_points))
            for point in turtle.line_points:
                list_line_x.append(point[0])
                list_line_y.append(point[1])
                list_line_z.append(point[2])
            # print("creating lines")
            if len(list_line_x)!=0:
                if str(idx) in self.lines_ax.keys():
                    if turtle.penmode()=="line":
                        self.lines_ax[str(idx)].set_data(list_line_x,list_line_y)
                        self.lines_ax[str(idx)].set_3d_properties(list_line_z, 'z')
                        self.lines_ax[str(idx)].set_markersize(turtle.size())
                        self.lines_ax[str(idx)].set_color(turtle.pen_dict["color"])
                        self.lines_ax[str(idx)].set_marker(turtle.pen_dict["marker"])
                        self.lines_ax[str(idx)].set_linewidth(float(turtle.pen_dict["linewidth"]))
                        self.lines_ax[str(idx)].set_markersize(float(turtle.pen_dict["markersize"]))
                    else: # poly
                        self.lines_ax[str(idx)].set_verts(turtle.line_points)
                        # ax_surface.set_3d_properties(list_z, 'z')
                        self.lines_ax[str(idx)].set_color(turtle.color())
                        self.lines_ax[str(idx)].set_linewidth(float(turtle.pen_dict["linewidth"]))
                else:
                    if turtle.penmode()=="line":
                        line_ax, =self.ax.plot(list_line_x,list_line_y,list_line_z,color=turtle.pen_dict["color"],
                                               marker=turtle.pen_dict["marker"],linestyle=turtle.pen_dict["linestyle"],linewidth=int(turtle.pen_dict["linewidth"]),markersize=int(turtle.pen_dict["markersize"]))
                    else: # poly
                        if len(list_line_x)<3:
                            line_ax=None
                        else:
                            line_ax = self.ax.plot_trisurf(list_line_x,list_line_y,list_line_z,
                                                           linewidth=float(turtle.pen_dict["linewidth"]),
                                                           color=turtle.pen_dict["color"], antialiased=True)


                    if line_ax!=None:
                        self.lines_ax[str(idx)] = line_ax
                    else:
                        if str(idx) in self.lines_ax:
                            self.lines_ax.pop(str(idx)).remove()
                    # print("plotting a line")
            else:
                if str(idx) in self.lines_ax.keys():
                    self.lines_ax.pop(str(idx))
            plt.draw()

        # set turtle visibility
        for idx in range(len(self.list_turtles)):
            if self.list_turtles[idx].isvisible()==False:
                ax_turtle=self.points_ax.pop(self.list_turtles[idx].id()).remove()
                # ax_turtle.remove()

        # create surfaces
        for surface in self.list_surfaces:
            # add()
            if len(surface.points())!=0:
                ax_surface=None
                list_x = []
                list_y = []
                list_z = []
                for point in surface.points():
                    if point[0] in list_x and point[1] in list_y and point[2] in list_z:
                        continue
                    list_x.append(point[0])
                    list_y.append(point[1])
                    list_z.append(point[2])
                if not surface.id() in self.surfaces_ax.keys():
                    try:
                        ax_surface=self.ax.plot_trisurf(list_x,list_y,list_z, linewidth=surface.linewidth(), color=surface.color(), antialiased=True)
                        self.surfaces_ax[surface.id()]=ax_surface
                    except Exception as err:
                        print(err)
                else:
                    ax_surface=self.surfaces_ax[surface.id()]
                    ax_surface.set_verts(surface.points())
                    # ax_surface.set_3d_properties(list_z, 'z')
                    ax_surface.set_color(surface.color())
                    ax_surface.set_linewidth(float(surface.linewidth()))
                    self.surfaces_ax[surface.id()]=ax_surface
            # die()
            if surface.is_dead:
                if surface.id() in self.surfaces_ax.keys():
                    self.surfaces_ax.pop(surface.id()).remove()
        # text
        for text in self.list_texts:
            if text.id() not in self.texts_ax.keys():
                text_ax=self.ax.text(text.xcor(), text.ycor(), text.zcor(), text.text(), color=text.color())
                self.texts_ax[text.id()]=text_ax
            else:
                self.texts_ax[text.id()].set_x(text.xcor())
                self.texts_ax[text.id()].set_y(text.ycor())
                self.texts_ax[text.id()].set_z(text.zcor())
                self.texts_ax[text.id()].set_color(text.color())
            # die()
            if text.is_dead:
                if text.id() in self.texts_ax.keys():
                    self.texts_ax.pop(text.id()).remove()

        # return modified artists
        return self.points_ax,self.lines_ax

    def run(self,frames=1000,go=None,setup=None,interval=500,repeat=False):
        # setup function
        self.setup=setup

        # go function, call by each step
        self.go = go

        # initialization of the world
        self.init()

        # print("test2")

        # start simulation
        ani = animation.FuncAnimation(self.fig, self.update_worlds, frames=frames, fargs=(self.points_ax,self.lines_ax),
                                      interval=interval,repeat=repeat
                                      )
        # show the world
        plt.show()

        self.is_start=False

    def bgcolor(self,color=None):
        if color!=None:
            self.fig.set_facecolor(color)
        return self.fig.get_facecolor()

    def bgcolor3d(self,color=None):
        if color!=None:
            self.ax.set_facecolor(color)
        return self.ax.get_facecolor()

    def screensize(self,w=-1,h=-1,dpi=200):
        if w!=-1 and h!=-1:
            self.fig.set_figwidth(w)
            self.fig.set_figheight(h)
            self.fig.set_dpi(dpi)
        return self.fig.get_figwidth,self.fig.get_figheight

    def clearscreen(self):
        self.is_deleting=True
        '''
        self.list_turtles=[]
        for k in list(self.points_ax.keys()):
            self.points_ax.pop(k).remove()
        for k in list(self.lines_ax.keys()):
            self.lines_ax.pop(k).remove()
        self.lines_ax={}
        self.points_ax={}
        '''

        for idx in range(len(self.list_turtles)):
            self.list_turtles[idx].die()
        self.is_deleting=False

    def resetscreen(self):
        return self.worldcoordinates(x_range=self.old_x_range,y_range=self.old_y_range,z_range=self.old_z_range)

    def worldcoordinates(self,x_range=None,y_range=None,z_range=None):
        if x_range!=None:
            self.x_range=x_range
            self.ax.set_xlim(x_range)
        if y_range!=None:
            self.ax.set_ylim(y_range)
            self.y_range = y_range
        if z_range!=None:
            self.ax.set_zlim(z_range)
            self.z_range = z_range
        return x_range,y_range,z_range

    def axis3d(self):
        return self.ax

    def figure(self):
        return self.fig

    def turtles(self,turtles=None):
        if turtles!=None:
            self.list_turtles=turtles
        return self.list_turtles

    def turtle_at(self,idx):
        return self.turtles()[idx]

    def turtle_find(self,turtle_id):
        for turtle in self.list_turtles:
            if turtle.id()==turtle_id:
                return turtle
        return None

    def texts(self,texts=None):
        if texts!=None:
            self.list_texts=texts
        return self.list_texts

    def text_at(self,idx):
        return self.list_texts[idx]

    def colorlist(self,colors):
        self.colors=colors

    def bye(self):
        print("Bye, world3D!")
        sys.exit(0)

    def exitonclick(self,flag=True):
        self.should_exit_on_click=flag

    def pressonclick(self,flag=True):
        self.should_exit_on_press=flag

    # input methods

    def textinput(self,title="Tips",prompt="Please input a string: "):
        app = Tk()
        app.withdraw()
        value = askstring(title=title,
                              prompt=prompt)
        app.destroy()
        self._last_input_value=value
        return value

    def floatinput(self,title="Tips",prompt="Please input a float: "):
        app = Tk()
        app.withdraw()
        value = askfloat(title=title,
                              prompt=prompt)
        app.destroy()
        self._last_input_value=value
        return value

    def last_input_value(self):
        return self._last_input_value

    def intinput(self,title="Tips",prompt="Please input a float: "):
        app = Tk()
        app.withdraw()
        value = askinteger(title=title,
                         prompt=prompt)
        app.destroy()
        self._last_input_value=value
        return value

    def message(self,title="Info",message=""):
        messagebox.showinfo(title,message)

    def error(self,title="Error",message=""):
        messagebox.showerror(title,message)

    def warning(self,title="Warning",message=""):
        messagebox.showwarning(title,message)

    def yesno(self,title="Yes|No",message=""):
        self._last_input_value= messagebox.askyesno(title, message)
        return self._last_input_value





