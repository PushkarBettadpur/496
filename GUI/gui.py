# Imports
import sys
import time
import math

from PyQt5.QtWidgets import (QApplication, QPushButton, QToolTip, QWidget, QLabel)
from PyQt5.QtGui import (QPainter, QColor, QIcon, QFont, QPalette, QBrush, QPixmap, QImage)
from PyQt5 import QtCore
from PyQt5.QtCore import (QSize, QTimer)

#############################################################################################
# Calss definition for the drawing grid
#############################################################################################

class CalculatePoints (QWidget):

    def __init__ (self, parent=None):
        super(CalculatePoints, self).__init__(parent)
        self.bufn = 10000
        self.buffer = [[None for x in range(2)] for y in range(self.bufn)]
        self.readPointer = 0
        self.writePointer = 0
        self.currentPosition = [0]*2
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.handleTimer)
        self.startTimer()

    def startTimer (self):
        self.timer.start(10)

    def handleTimer (self):
        if (self.buffer[self.readPointer][0] != None):
            posX = self.buffer[self.readPointer][0]
            posY = self.buffer[self.readPointer][1]
            self.buffer[self.readPointer][0] = None
            self.buffer[self.readPointer][1] = None
            if (self.readPointer < (self.bufn - 1)):
                self.readPointer += 1
            else:
                readPointer = 0
        else:
            posX = self.currentPosition[0]
            posY = self.currentPosition[1]
        print (posX, posY)

    def setCurrentPosition (self, posX, posY):
        self.currentPosition[0] = posX
        self.currentPosition[1] = posY

    def writePoint (self, posX, posY):
        while True:
            if (self.buffer[self.writePointer][0] == None):
                self.buffer[self.writePointer][0] = posX
                self.buffer[self.writePointer][1] = posY
                if (self.writePointer < (self.bufn - 1)):
                    self.writePointer += 1
                else:
                    self.writePointer = 0
                break

    def setPoints (self, start, end):
        x1 = start.x()
        y1 = -start.y()
        x2 = end.x()
        y2= -end.y()
        dx = x2 - x1
        dy = y2 - y1
        if (math.fabs(dx) > math.fabs(dy)):
            s = dy/dx
            y = y1
            for x in range(x1,x2):
                self.writePoint(math.ceil(x), math.ceil(y))
                y = y + s
        elif (math.fabs(dx) < math.fabs(dy)):
            s = dx/dy
            x = x1
            if (y1 < y2):
                for y in range(y1,y2):
                    self.writePoint(math.ceil(x), math.ceil(y))
                    x = x + s
            elif (y1 > y2):
                for y in range(y1,y2):
                    self.writePoint(math.ceil(x), math.ceil(y))
                    x = x - s

    def setPath (self, start, path, end):
        self.setPoints(start, path[0])
        for i in range(1,len(path)):
            self.setPoints(path[i], path[i-1])
        self.setPoints(path[len(path)-1], end)

    #def setDirection (self, dir):

#############################################################################################
# Calss definition for the drawing grid
#############################################################################################

class Grid (QPushButton):

    def __init__ (self, parent=None):
        super(Grid, self).__init__(parent)
        self.resize(826,478)
        self.move(856,10)
        self.startCircle = QLabel("", self)
        self.endCircle = QLabel("", self)
        self.pathCircle = []
        self.resetGrid()

    def resetGrid (self):
        self.setStyleSheet("background: transparent; border-image: ;")
        self.initPoints()
        self.removeEventFilter(self)
        self.captureSignal = None
        self.startPoint = None
        self.endPoint = None
        self.pathPoints = []

    def initPoints (self):
        for point in self.pathCircle:
            point.hide()
        del self.pathCircle[:]
        self.startCircle.move(0,0)
        self.endCircle.move(0,0)
        self.startCircle.resize(20,20)
        self.endCircle.resize(20,20)
        self.startCircle.setStyleSheet("border-image: url(startPoint.png);")
        self.endCircle.setStyleSheet("border-image: url(endPoint.png);")
        self.startCircle.hide()
        self.endCircle.hide()

    def moveStartPoint (self, pos):
        self.startCircle.move(pos.x(),pos.y())
        self.startCircle.show()

    def moveEndPoint (self, pos):
        self.endCircle.move(pos.x(),pos.y())
        self.endCircle.show()

    def eventFilter (self, object, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if (self.captureSignal == 0):
                self.startPoint = event.pos()
                self.moveStartPoint(event.pos())
            elif (self.captureSignal == 1):
                self.endPoint = event.pos()
                self.moveEndPoint(event.pos())
            elif (self.captureSignal == 2):
                self.startPoint = event.pos()
                self.moveStartPoint(event.pos())
            return True
        elif event.type() == QtCore.QEvent.MouseMove:
            if (self.captureSignal == 2):
                self.pathPoints.append(event.pos())
                point = QLabel("", self)
                point.move(event.pos().x(),event.pos().y())
                point.resize(5,5)
                point.setStyleSheet("border-image: url(pathPoint.png);")
                point.show()
                self.pathCircle.append(point)
            return True
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if (self.captureSignal == 2):
                self.endPoint = event.pos()
                self.moveEndPoint(event.pos())
                self.turnOffGrid()
            return True

        return False;

    def turnOnGrid (self, signal):
        self.captureSignal = signal
        self.installEventFilter(self)
        self.setStyleSheet("background: transparent; border-image: url(grid.png);")

    def turnOffGrid (self):
        self.removeEventFilter(self)
        self.setStyleSheet("background: transparent; border-image: ;")

    def getStartPoint (self):
        return self.startPoint

    def getEndPoint (self):
        return self.endPoint

    def getPathPoints (self):
        return self.pathPoints

#############################################################################################
# Calss definition for the the side buttons
#############################################################################################

class SideButton (QPushButton):

    def __init__ (self, parent=None):
        super(SideButton, self).__init__(parent)
        self.setFont(QFont('Times', 17))
        self.resize(150,115)
        self.resetButton()

    def resetButton (self):
        self.setStyleSheet("border-image: url(sideButtonOff.png); color: white;")
        self.removeEventFilter(self)
        self.captureSignal = None

    def eventFilter (self, object, event):

        if event.type() == QtCore.QEvent.HoverMove:
            self.setStyleSheet("border-image: url(sideButtonHover.png); color: white;")
            return True

        elif event.type() == QtCore.QEvent.HoverLeave:
            self.setStyleSheet("border-image: url(sideButtonOn.png); color: white;")
            return True

        elif event.type() == QtCore.QEvent.MouseButtonPress:
            if object.pos().y() == 40:
                self.handleButton5Press()
            elif object.pos().y() == 190:
                self.handleButton6Press()
            elif object.pos().y() == 340:
                self.handleButton7Press()
            return True

        return False;

    def turnOnButton (self, signal):
        self.captureSignal = signal
        self.setStyleSheet("border-image: url(sideButtonOn.png); color: white;")
        self.installEventFilter(self)

    def turnOffButton (self):
        self.removeEventFilter(self)
        self.setStyleSheet("border-image: url(sideButtonOff.png); color: white;")

    def handleButton5Press (self):
        startPoint = mainWindow.frame3.getStartPoint()
        if (startPoint != None):
            mainWindow.frame3.turnOnGrid(1)
            mainWindow.instr.changeText("Click on the endpoint in the grid and hit the 'Send' button.")
            self.turnOffButton()
            mainWindow.button6.turnOnButton(0)
        else:
            mainWindow.instr.changeText("Please select a startpoint before pressing the 'Fix' button.")

    def handleButton6Press (self):
        if (self.captureSignal == 0):
            endPoint = mainWindow.frame3.getEndPoint()
            if (endPoint != None):
                startPoint = mainWindow.frame3.getStartPoint()
                mainWindow.button7.handleButton7Press()
                mainWindow.sendPoints.setPoints(startPoint, endPoint)
                time.sleep(2)
            else:
                mainWindow.instr.changeText("Please select an endpoint before pressing the 'Send' button.")
        elif (self.captureSignal == 1):
            startPoint = mainWindow.frame3.getStartPoint()
            if (startPoint != None):
                endPoint = mainWindow.frame3.getEndPoint()
                pathPoints = mainWindow.frame3.getPathPoints()
                mainWindow.button7.handleButton7Press()
                mainWindow.sendPoints.setPath(startPoint, pathPoints, endPoint)
                time.sleep(2)
            else:
                mainWindow.instr.changeText("Please enter a path before pressing the 'Send' button.")                

    def handleButton7Press (self):
        mainWindow.button1.resetButton()
        mainWindow.button2.resetButton()
        mainWindow.button3.resetButton()
        mainWindow.button4.resetButton()
        mainWindow.button5.resetButton()
        mainWindow.button6.resetButton()
        mainWindow.button7.resetButton()
        mainWindow.frame3.resetGrid()
        mainWindow.instr.changeText("")

#############################################################################################
# Class definition for the manual control button
#############################################################################################

class ManualButton (QPushButton):

    def __init__ (self, parent=None):
        super(ManualButton, self).__init__(parent)
        self.resize(166,160)
        self.resetButton()

    def resetButton (self):
        self.basePoint = {'x': 332, 'y': 750}
        self.move(332,750)
        self.setStyleSheet("border-image: url(manualButtonOff.png);")
        self.removeEventFilter(self)

    def eventFilter (self, object, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            return True
        elif event.type() == QtCore.QEvent.MouseMove:
            posX = self.mapToParent(event.pos()).x()
            posY = self.mapToParent(event.pos()).y()
            relX = 415 - posX
            relY = 830 - posY
            dirX = 0
            dirY = 0
            if (math.ceil(math.sqrt(math.pow(relX,2) + math.pow(relY,2))) >= 10):
                # Calculate the position of the button
                if (math.ceil(math.sqrt(math.pow(relX,2) + math.pow(relY,2))) <= 40):
                    self.basePoint['x'] = 332 - relX
                    self.basePoint['y'] = 750 - relY
                else:
                    self.basePoint['x'] = 332 - math.floor(relX/math.sqrt(math.pow(relX,2) + math.pow(relY,2))*40)
                    self.basePoint['y'] = 750 - math.floor(relY/math.sqrt(math.pow(relX,2) + math.pow(relY,2))*40)
                self.move(self.basePoint['x'],self.basePoint['y'])

                # Calculate the direction of motion
                if (relX != 0):
                    angle = math.atan(-relY/relX)*180/math.pi
                    if (relX > 0):
                        angle = angle + 180
                    elif (relY < 0):
                        angle = angle + 360
                    if ((angle <= 67.5) or (angle >= 292.5)):
                        dirX = 1
                    elif ((angle >= 112.5) and (angle <= 247.5)):
                        dirX = -1
                    if ((angle >= 22.5) and (angle <= 157.5)):
                        dirY = 1
                    elif ((angle >= 202.5) and (angle <= 337.5)):
                        dirY = -1
            print (dirX, dirY)
            # Do the control
            # Send the direction
            return True
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            self.move(332,750)
            return True
        return False;

    def turnOnButton (self):
        self.setStyleSheet("border-image: url(manualButtonOn.png); color: white;")
        self.installEventFilter(self)

    def turnOffButton (self):
        self.removeEventFilter(self)
        self.setStyleSheet("border-image: url(manualButtonOff.png); color: white;")

#############################################################################################
# Class definition for the three main control buttons
#############################################################################################

class ControlButton (QPushButton):

    def __init__ (self, parent=None):
        super(ControlButton, self).__init__(parent)
        self.setFont(QFont('Times', 17))
        self.resize(150,115)
        self.resetButton()

    def resetButton (self):
        self.setStyleSheet("border-image: url(controlButton.png); color: white;")
        self.installEventFilter(self)

    def eventFilter (self, object, event):

        if event.type() == QtCore.QEvent.HoverMove:
            self.setStyleSheet("border-image: url(controlButtonHover.png); color: white;")
            return True

        elif event.type() == QtCore.QEvent.HoverLeave:
            self.setStyleSheet("border-image: url(controlButton.png); color: white;")
            return True

        elif event.type() == QtCore.QEvent.MouseButtonPress:
            self.setStyleSheet("border-image: url(controlButtonClicked.png); color: white;")
            if object.pos().x() == 143:
                self.handleButton1Press()
            elif object.pos().x() == 343:
                self.handleButton2Press()
            elif object.pos().x() == 543:
                self.handleButton3Press()
            return True

        return False;


    def turnOnButton (self):
        self.setStyleSheet("border-image: url(controlButton.png); color: white;")
        self.installEventFilter(self)

    def turnOffButton (self):
        self.removeEventFilter(self)
        self.setStyleSheet("border-image: url(sideButtonOff.png); color: white;")

    def handleButton1Press (self):
        self.removeEventFilter(self)
        mainWindow.button2.turnOffButton()
        mainWindow.button3.turnOffButton()
        mainWindow.button5.turnOnButton(2)
        mainWindow.button7.turnOnButton(2)
        mainWindow.frame3.turnOnGrid(0)
        mainWindow.instr.changeText("Click on the startpoint in the grid and hit the 'Fix' button.")

    def handleButton2Press (self):
        self.removeEventFilter(self)
        mainWindow.button1.turnOffButton()
        mainWindow.button3.turnOffButton()
        mainWindow.button6.turnOnButton(1)
        mainWindow.button7.turnOnButton(2)
        mainWindow.frame3.turnOnGrid(2)
        mainWindow.instr.changeText("Draw the path of the grid and hit the 'Send' button.")

    def handleButton3Press (self):
        self.removeEventFilter(self)
        mainWindow.button1.turnOffButton()
        mainWindow.button2.turnOffButton()
        mainWindow.button4.turnOnButton()
        mainWindow.button7.turnOnButton(2)
        mainWindow.instr.changeText("Press, hold and drag the blue button below for manual control. Release the button to stop.")

#############################################################################################
# Class definition for the instructions panel
#############################################################################################

class InstrPanel (QLabel):
    def __init__(self,parent=None):
        super(InstrPanel, self).__init__(parent)
        self.setWordWrap(True)
        self.setFont(QFont('Courier', 15))
        self.setStyleSheet("background: transparent; color: white;")
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.resize(683,136)
        self.move(82,501)
        self.text = ''
        self.index = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.handleTimer)

    def changeText(self, text):
        self.text = text
        self.index = 0
        self.timer.start(18)

    def handleTimer(self):
        self.index += 1
        self.setText(self.text[:self.index])
        if self.index > len(self.text):
            self.timer.stop()

#############################################################################################
# Class definition for the main window
#############################################################################################

class Window (QWidget):

    def __init__ (self):
        super().__init__()
        self.initUX()

    def initUX (self):

        QToolTip.setFont(QFont('Times', 14))

        # Set window size, title and icon
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setWindowTitle('TARDIS UI')
        self.setWindowIcon(QIcon('rover.png'))
        
        # Set main window's background
        bgImage = QImage("mainWindow.png")
        bgImage = bgImage.scaled(QSize(1919, 986))   
        palette	= QPalette()
        palette.setBrush(QPalette.Background,QBrush(bgImage))
        self.setPalette(palette)

        # Initialize the Instruction Panel
        self.initTextFrames()

        # Initialize all buttons
        self.initButtons()

        # Initialize video frames
        self.initFrames()

        # Start the timer to send points
        self.sendPoints = CalculatePoints(self)

        # Display the window
        self.show()

    def initTextFrames (self):
        self.instr = InstrPanel(self)

        self.tempHead = QLabel("<b>On-Site Temperature:</b>", self)
        self.tempHead.setWordWrap(True)
        self.tempHead.setFont(QFont('Courier', 12))
        self.tempHead.setStyleSheet("background: transparent; color: white;")
        self.tempHead.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.tempHead.resize(170,60)
        self.tempHead.move(1740,501)

        self.temp = QLabel("", self)
        self.temp.setWordWrap(True)
        self.temp.setFont(QFont('Courier', 32))
        self.temp.setStyleSheet("background: transparent; color: white;")
        self.temp.setText("25°C")
        self.temp.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.temp.resize(170,80)
        self.temp.move(1740,570)

    def initButtons (self):
        # Set "Enter Points" button
        self.button1 = ControlButton(self)
        self.button1.setText('Enter\nPoints')
        self.button1.move(143,277)

        # Set "Draw Path" button
        self.button2 = ControlButton(self)
        self.button2.setText('Draw\nPath')
        self.button2.move(343,277)
        
        # Set "Manual Control" button
        self.button3 = ControlButton(self)
        self.button3.setText('Manual\nControl')
        self.button3.move(543,277)

        # Set "Round Manual Control" button
        self.button4 = ManualButton(self)

        # Set "Fix" button
        self.button5 = SideButton(self)
        self.button5.setText('Fix')
        self.button5.move(1740,40)

        # Set "Send" button
        self.button6 = SideButton(self)
        self.button6.setText('Send')
        self.button6.move(1740,190)
        
        # Set "Cancel" button
        self.button7 = SideButton(self)
        self.button7.setText('Cancel')
        self.button7.move(1740,340)

    def initFrames (self):
        # Set "Overhead Camera" video frame
        self.frame1 = QLabel("", self)
        self.frame1.setStyleSheet("background: grey;")
        self.frame1.resize(826,478)
        self.frame1.move(856,10)

        # Set "Onboard Camera" video frame
        self.frame2 = QLabel("", self)
        self.frame2.setStyleSheet("background: grey;")
        self.frame2.resize(826,478)
        self.frame2.move(856,498)

        # Frame for the grid superimposed on the overhead footage
        self.frame3 = Grid(self)

#############################################################################################
# Main function initialization
#############################################################################################

if __name__ == '__main__':
    
    # Initialize the application 
    mainApp = QApplication(sys.argv)

    # Initialize the main window object
    mainWindow = Window()

    # Exit command
    sys.exit(mainApp.exec_())