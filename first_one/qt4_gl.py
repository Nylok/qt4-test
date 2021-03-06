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

from PyQt4 import QtCore, QtGui, QtOpenGL

try:
    from OpenGL.GL import *
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL textures",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)

import textures_rc



class GLWidget(QtOpenGL.QGLWidget):

    clicked = QtCore.pyqtSignal()

    PROGRAM_VERTEX_ATTRIBUTE, PROGRAM_TEXCOORD_ATTRIBUTE = range(2)

    vsrc = """
attribute highp vec4 vertex;
attribute mediump vec4 texCoord;
varying mediump vec4 texc;
uniform mediump mat4 matrix;
void main(void)
{
    gl_Position = matrix * vertex;
    texc = texCoord;
}
"""

    fsrc = """
uniform sampler2D texture;
varying mediump vec4 texc;
void main(void)
{
    gl_FragColor = texture2D(texture, texc.st);
}
"""

    coords = (
        (( +1, -1, -1 ), ( -1, -1, -1 ), ( -1, +1, -1 ), ( +1, +1, -1 )),
        (( +1, +1, -1 ), ( -1, +1, -1 ), ( -1, +1, +1 ), ( +1, +1, +1 )),
        (( +1, -1, +1 ), ( +1, -1, -1 ), ( +1, +1, -1 ), ( +1, +1, +1 )),
        (( -1, -1, -1 ), ( -1, -1, +1 ), ( -1, +1, +1 ), ( -1, +1, -1 )),
        (( +1, -1, +1 ), ( -1, -1, +1 ), ( -1, -1, -1 ), ( +1, -1, -1 )),
        (( -1, -1, +1 ), ( +1, -1, +1 ), ( +1, +1, +1 ), ( -1, +1, +1 ))
    )

    def __init__(self, parent=None, shareWidget=None):
        super(GLWidget, self).__init__(parent, shareWidget)

        self.clearColor = QtCore.Qt.black
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.clearColor = QtGui.QColor()
        self.lastPos = QtCore.QPoint()

        self.program = None
        self.blend_r = 0.1
	self.blend_g = 0.1
	self.blend_b = 0.1
	self.blend_a = 0.1

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
        self.makeObject()

        #MY Changes
        #Disable Depth test and face culling so it can blend layers at diferent depths
        #glEnable(GL_DEPTH_TEST)
        #glEnable(GL_CULL_FACE)
        
        #Enables blending and adds blending functions
        glEnable(GL_BLEND)
        glBlendFunc(GL_CONSTANT_COLOR,GL_ONE_MINUS_CONSTANT_COLOR)
	
	
        vshader = QtOpenGL.QGLShader(QtOpenGL.QGLShader.Vertex, self)
        vshader.compileSourceCode(self.vsrc)

        fshader = QtOpenGL.QGLShader(QtOpenGL.QGLShader.Fragment, self)
        fshader.compileSourceCode(self.fsrc)

        self.program = QtOpenGL.QGLShaderProgram(self)
        self.program.addShader(vshader)
        self.program.addShader(fshader)
        self.program.bindAttributeLocation('vertex',
                self.PROGRAM_VERTEX_ATTRIBUTE)
        self.program.bindAttributeLocation('texCoord',
                self.PROGRAM_TEXCOORD_ATTRIBUTE)
        self.program.link()

        self.program.bind()
        self.program.setUniformValue('texture', 0)

        self.program.enableAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE)
        self.program.enableAttributeArray(self.PROGRAM_TEXCOORD_ATTRIBUTE)
        self.program.setAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE,
                self.vertices)
        self.program.setAttributeArray(self.PROGRAM_TEXCOORD_ATTRIBUTE,
                self.texCoords)

    def paintGL(self):
        self.qglClearColor(self.clearColor)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glBlendColor(self.blend_r,self.blend_g,self.blend_b,self.blend_a)
	m = QtGui.QMatrix4x4()
        m.ortho(-0.5, 0.5, 0.5, -0.5, 4.0, 15.0)
        m.translate(0.0, 0.0, -10.0)
        m.rotate(self.xRot / 16.0, 1.0, 0.0, 0.0)
        m.rotate(self.yRot / 16.0, 0.0, 1.0, 0.0)
        m.rotate(self.zRot / 16.0, 0.0, 0.0, 1.0)

        self.program.setUniformValue('matrix', m)

        for i in range(6):
            glBindTexture(GL_TEXTURE_2D, self.textures[i])
            glDrawArrays(GL_TRIANGLE_FAN, i * 4, 4)

    def resizeGL(self, width, height):
        side = min(width, height)
        glViewport((width - side) / 2, (height - side) / 2, side, side)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            self.rotateBy(8 * dy, 8 * dx, 0)
        elif event.buttons() & QtCore.Qt.RightButton:
            self.rotateBy(8 * dy, 0, 8 * dx)

        self.lastPos = event.pos()

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    def makeObject(self):
        self.textures = []
        self.texCoords = []
        self.vertices = []

        for i in range(6):
            self.textures.append(
                    self.bindTexture(
                            QtGui.QPixmap(':/images/side%d.png' % (i + 1))))

            for j in range(4):
                self.texCoords.append(((j == 0 or j == 3), (j == 0 or j == 1)))

                x, y, z = self.coords[i][j]
                self.vertices.append((0.2 * x, 0.2 * y, 0.2 * z))

    def value_r(self,value):
	self.blend_r = float(value)/100.0

    def value_g(self,value):
	self.blend_b = float(value)/100.0
	
    def value_b(self,value):
	self.blend_g = float(value)/100.0

    def value_a(self,value):
	self.blend_a = float(value)/100.0
	
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

                widget = GLWidget(None, None)
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

        self.slider_one = QtGui.QSlider(QtCore.Qt.Horizontal)
	#self.slider_one.setGeometry(QtCore.QRect(0, 255, 60, 265))
        self.slider_one.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider_one.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider_one.setTickInterval(100)
        self.slider_one.setSingleStep(1)
        self.slider_one.setMinimum(1)
        
        self.slider_two = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider_two.setGeometry(QtCore.QRect(20, 40, 140, 160))
        self.slider_two.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider_two.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider_two.setTickInterval(100)
        self.slider_two.setSingleStep(1)
        self.slider_two.setMinimum(1)
        
        self.slider_tree = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider_tree.setGeometry(QtCore.QRect(20, 40, 140, 160))
        self.slider_tree.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider_tree.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider_tree.setTickInterval(100)
        self.slider_tree.setSingleStep(1)
        self.slider_tree.setMinimum(1)
        
        self.slider_four = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider_four.setGeometry(QtCore.QRect(20, 40, 140, 160))
        self.slider_four.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider_four.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider_four.setTickInterval(100)
        self.slider_four.setSingleStep(1)
        self.slider_four.setMinimum(1)
        
        self.slider_one.valueChanged.connect(self.currentGlWidget.value_r)
        self.slider_two.valueChanged.connect(self.currentGlWidget.value_g)
        self.slider_tree.valueChanged.connect(self.currentGlWidget.value_b)
        self.slider_four.valueChanged.connect(self.currentGlWidget.value_a)
        mainLayout.addWidget(self.slider_one,2,0)
        mainLayout.addWidget(self.slider_two,3,0)
        mainLayout.addWidget(self.slider_tree,4,0)
        mainLayout.addWidget(self.slider_four,5,0)
        self.setLayout(mainLayout)
        self.setWindowTitle("Textures")

    def setCurrentGlWidget(self):
	
        self.currentGlWidget = self.sender()
        self.slider_one.valueChanged.connect(self.currentGlWidget.value_r)
        self.slider_two.valueChanged.connect(self.currentGlWidget.value_g)
        self.slider_tree.valueChanged.connect(self.currentGlWidget.value_b)
        self.slider_four.valueChanged.connect(self.currentGlWidget.value_a)

    def rotateOneStep(self):
        if self.currentGlWidget:
            self.currentGlWidget.rotateBy(+2 * 16, +2 * 16, -1 * 16)
          
            
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    
    
    sys.exit(app.exec_())
