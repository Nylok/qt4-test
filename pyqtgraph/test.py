#############################################################################
##
## Copyright (C) 2010 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


import sys

from PyQt4 import QtCore, QtGui
from OpenGL.GL import *
import pyqtgraph.opengl as gl
import numpy as np

daata = np.empty([25,25,25,4])

for x in range(0,25):
  for y in range(0,25):
    for z in range(0,25):
      for color in range(0,4):
	daata[x,y,z,color] = np.random.power(2.0)*255


class GLViewWidget(gl.GLViewWidget):

    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(GLViewWidget, self).__init__()

        self.clearColor = QtCore.Qt.black
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.clearColor = QtGui.QColor()
        self.lastPos = QtCore.QPoint()

        self.blend_v = 0
	
        self.opts['distance']=35
        self.opts['center']= QtGui.QVector3D(12.5,12.5,12.5)
        
	self.addItem(gl.GLVolumeItem(daata,smooth=False))

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(200, 200)

    def rotateBy(self, xAngle, yAngle, zAngle):
        self.xRot += xAngle
        self.yRot += yAngle
        self.zRot += zAngle
        self.updateGL()

    def setClearColor(self, color):
        self.clearColor = color
        self.updateGL()

    def initializeGL(self):
        c = self.clearColor.getRgbF()
	glClearColor(c[0],c[1],c[2],c[3])
	

    def setProjection(self):
          ## Create the projection matrix
          glMatrixMode(GL_PROJECTION)
          glLoadIdentity()
          w = self.width()
          h = self.height()
          dist = self.opts['distance']
          fov = self.opts['fov']
          
          nearClip = dist * 0.001
          farClip = dist * 1000.
          
          r = nearClip * np.tan(fov * 0.5 * np.pi / 180.)
          t = r * h / w
          glFrustum( -r, r, -t, t, nearClip, farClip)
          
    def setModelview(self):
         glMatrixMode(GL_MODELVIEW)
         glLoadIdentity()
         glTranslatef( 0.0, 0.0, -self.opts['distance'])
         glRotatef(self.opts['elevation']-90, 1, 0, 0)
         glRotatef(self.opts['azimuth']+90, 0, 0, -1)
         center = self.opts['center']
         glTranslatef(-center.x(), -center.y(), -center.z())
          
          
    def paintGL(self):
        self.setProjection()
        self.setModelview()
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        self.drawItemTree()
        
          
    def drawItemTree(self, item=None):
	for i in self.items:
	    if i==None:
		continue
	    else:
		if self.blend_v == 1:
		    i.setGLOptions('additive')
		
		if self.blend_v == 2:
		    i.setGLOptions('translucent')
		    
		if self.blend_v == 0:
		    i.setGLOptions('opaque')
		
		    
		i.paint()
                  

    def resizeGL(self, width, height):
        side = min(width, height)
        glViewport((width - side) / 2, (height - side) / 2, side, side)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
	self.orbit(dx,dy)
	
        if event.buttons() & QtCore.Qt.LeftButton:
            self.rotateBy(8 * dy, 8 * dx, 0)
        elif event.buttons() & QtCore.Qt.RightButton:
            self.rotateBy(8 * dy, 0, 8 * dx)

        self.lastPos = event.pos()

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    #def makeObject(self):
        

    def value_additive(self,value):
	self.blend_v = 1

    def value_translucent(self,value):
	self.blend_v = 2
	
    def value_opaque(self,value):
	self.blend_v = 0

	
class Window(QtGui.QWidget):
    NumRows = 2
    NumColumns = 3

    def __init__(self):
        super(Window, self).__init__()

        mainLayout = QtGui.QGridLayout()
        self.glWidgets = []

        for i in range(Window.NumRows):
            row = []

            for j in range(Window.NumColumns):
                clearColor = QtGui.QColor()
                clearColor.setHsv(((i * Window.NumColumns) + j) * 255
                                  / (Window.NumRows * Window.NumColumns - 1),
                                  255, 63)

                widget = GLViewWidget()
                widget.setClearColor(clearColor)
                widget.rotateBy(+42 * 16, +42 * 16, -21 * 16)
                mainLayout.addWidget(widget, i, j)

                widget.clicked.connect(self.setCurrentGlWidget)

                row.append(widget)

            self.glWidgets.append(row)

        

        self.currentGlWidget = self.glWidgets[0][0]

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.rotateOneStep)
        timer.start(20)

        
	self.button_additive = QtGui.QPushButton('additive', self)
        self.button_translucent = QtGui.QPushButton('translucent', self)
        self.button_opaque = QtGui.QPushButton('opaque', self)
        
        mainLayout.addWidget(self.button_additive,2,0)
	mainLayout.addWidget(self.button_translucent,3,0)
        mainLayout.addWidget(self.button_opaque,4,0)
        
        self.button_additive.clicked.connect(self.currentGlWidget.value_additive)
        self.button_translucent.clicked.connect(self.currentGlWidget.value_translucent)
        self.button_opaque.clicked.connect(self.currentGlWidget.value_opaque)
        
        self.setLayout(mainLayout)
        self.setWindowTitle("Textures")

    def setCurrentGlWidget(self):
	self.button_additive.clicked.disconnect(self.currentGlWidget.value_additive)
        self.button_translucent.clicked.disconnect(self.currentGlWidget.value_translucent)
        self.button_opaque.clicked.disconnect(self.currentGlWidget.value_opaque)
        self.currentGlWidget = self.sender()
        self.button_additive.clicked.connect(self.currentGlWidget.value_additive)
        self.button_translucent.clicked.connect(self.currentGlWidget.value_translucent)
        self.button_opaque.clicked.connect(self.currentGlWidget.value_opaque)

    def rotateOneStep(self):
        if self.currentGlWidget:
            self.currentGlWidget.rotateBy(+2 * 16, +2 * 16, -1 * 16)
          
            
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    
    
    sys.exit(app.exec_())
