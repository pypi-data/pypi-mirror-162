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

from lightlogo.world3D import *
'''
    playground of LightLogo 3D
'''
class play3D:

    def __init__(self):
        pass

    def run(self,first_turtle,frames=1000,repeat=True,interval=500):
        self.w3d = world3D(x_range=[-10, 10], y_range=[-10, 10], z_range=[-10, 10], title="A 3D playground in LightLogo", )
        self.w3d.create(style="seaborn-ticks")

        def setup(world):
            list_turtles = [turtle3D(xyz=[0, 0, 0], color='blue', shape='.', size=10) for _ in range(1)]
            world.turtles(list_turtles)

        def go(frame,world):
            turtle=world.turtle_at(0)
            if first_turtle!=None:
                turtle=first_turtle(turtle)
            world.turtles()[0]=turtle

        self.w3d.run(go=go,setup=setup,interval=interval,frames=frames,repeat=repeat)

    def run_once(self,first_turtle):
        self.run(first_turtle=first_turtle,repeat=False,frames=1)

play3d=play3D()
world=play3d.w3d
turtle=world.turtle_at(0)

def start():
    pass

def fd(d):
    turtle.fd(d)

def left(a):
    turtle.left(a)


def up(a):
    turtle.up(a)

def end():
    pass