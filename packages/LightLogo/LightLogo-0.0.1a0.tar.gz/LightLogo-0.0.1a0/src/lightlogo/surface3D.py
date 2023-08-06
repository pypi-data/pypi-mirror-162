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

'''
    Surface in a 3D world
'''
class surface3D:

    surface_counter = 0

    @staticmethod
    def surface_id():
        surface3D.surface_counter = surface3D.surface_counter + 1
        return surface3D.surface_counter + 1

    def __init__(self,points,color="blue",line_width=0.2):
        self._points=points
        self._color=color
        self._id=surface3D.surface_id()
        self.is_dead=False
        self._line_width=line_width

    def points(self):
        return self._points

    def color(self):
        return self._color

    def id(self):
        return str(self._id)

    def set_point(self,idx,point):
        self._points[idx]=point

    def die(self):
        self.is_dead=True

    def linewidth(self,w=-1):
        if w!= -1:
            self._line_width=w
        return self._line_width