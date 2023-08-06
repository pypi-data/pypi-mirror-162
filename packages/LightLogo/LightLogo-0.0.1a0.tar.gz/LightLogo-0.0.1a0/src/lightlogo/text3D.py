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

class text3D:

    text_counter = 0

    @staticmethod
    def text_id():
        text3D.text_counter = text3D.text_counter + 1
        return text3D.text_counter + 1

    def __init__(self,text,x=0,y=0,z=0,xyz=None,color='black'):
        self._text=text
        self._color=color
        self.x=x
        self.y=y
        self.z=z
        if xyz!=None:
            self.x=xyz[0]
        if xyz!=None:
            self.y=xyz[1]
        if xyz!=None:
            self.z=xyz[2]
        self._id=text3D.text_id()
        self.is_dead=False

    def die(self):
        self.is_dead=True

    def id(self):
        return self._id

    def xcor(self):
        return self.x

    def ycor(self):
        return self.y

    def zcor(self):
        return self.z

    def position(self):
        return [self.x,self.y,self.z]

    def text(self,text=None):
        if text!=None:
            self._text=text
        return self._text

    def color(self,color=None):
        if color!=None:
            self._color=color
        return self._color