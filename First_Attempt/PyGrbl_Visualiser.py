#!/usr/bin/python3.2

"""
Toolpath_Visualiser

"""

from tkinter import *
from tkinter import ttk

import time, re

import math
import tkinter.font



##
#
# DEGUG MODE SETTING
#

debugMode = 0 # 0=None, 1=High Level Only, 2 = Everything

##
#
# GLOBAL VARIABLES
#

screenWidth = 800
screenHeight = 500
wpadx = 5
wpady = 5


#widget font

#text box font
textboxFont = ("Helvetica", 14)

tablecols = ['line', 'gCode IN', 'Result', 'Comment', 'gCode OUT']
tablerows = []

gCodeData = [[], [], [], []] # [0] = gCodeIN, [1 / 2] = preproc result/comment, [3] = gCodeOUT


class Toolpath_VisualiserApp(Frame):
    def __init__(self, master, toolpath = None):
        super(Toolpath_VisualiserApp, self).__init__(master)
        self.master.title("Toolpath Visualiser App")

        screenWidth = 600
        screenHeight = 300 - 30
        defaultXaxisMkr = 0.05 # % X in -ve
        defaultYaxisMkr = 0.05 # % Y in -ve
        defaultZoom = 1
        self.defaultSpeed = 0.1 # delay (sec) when drawing toolpath

        self.master.geometry(str(screenWidth) + "x" + str(screenHeight + 30))
        self.grid(column = 0, row = 0)

        myVisualiser = Toolpath_Visualiser(self)
        myVisualiser.drawToolpath(toolpath)
        myVisualiser.grid()
        
        self.update_idletasks()


class Toolpath_Visualiser(Frame):    
    def __init__(self, master, toolpath = None):
        Frame.__init__(self, master = master)
        screenWidth = 600
        screenHeight = 300 - 30
        defaultXaxisMkr = 0.05 # % X in -ve
        defaultYaxisMkr = 0.05 # % Y in -ve
        defaultZoom = 1
        self.defaultSpeed = 0.1 # delay (sec) when drawing toolpath

        self.zoom =defaultZoom
        self.zooming = False
        self.xaxisMarker = defaultXaxisMkr # ratio of axis to be -ve
        self.yaxisMarker = defaultYaxisMkr
        self.speed = self.defaultSpeed

        self.createVisualWidgets()
        self.grid()

        self.quickdraw = False
        #self.visualiseCode()


    def createVisualWidgets(self):
        frame = self

        # Draw Button
        frame.drawButt = Button(frame)
        frame.drawButt.configure(text = "Draw", command = lambda: self.drawToolpath(), highlightcolor = "white")
        frame.drawButt.grid(row = 0, column = 0, sticky = E)
        frame.drawButt.configure(state = "disabled")

        # gCode Block Text
        self.blockText = Text(frame, width = 30, height = 1, font = textboxFont)
        self.blockText.configure(highlightcolor = "white")
        self.blockText.grid(row = 0, column = 1, padx = wpadx, pady = wpady, sticky = W)
        self.blockText.configure(state = "disabled")
        
        # Pause Button
        frame.pauseButt = Button(frame)
        frame.pauseButt.configure(text = "Pause", command = lambda: self.setPause())
        frame.pauseButt.grid(row = 0, column = 2, sticky = W)
        frame.pauseButt.configure(state = "disabled")

        # Zoom options
        frame.zoomInButt = Button(frame)
        frame.zoomInButt.configure(text = "Zoom +", command = lambda: self.doZoom('in'))
        frame.zoomInButt.grid(row = 0, column = 3) 
        frame.zoomInButt.configure(state = "disabled")

        frame.zoomOutButt = Button(frame)
        frame.zoomOutButt.configure(text = "Zoom -", command = lambda: self.doZoom('out'))
        frame.zoomOutButt.grid(row = 0, column = 4)
        frame.zoomOutButt.configure(state = "disabled")

        self.createWorkArea()
        

    def createWorkArea(self):
        frame = self
        
        if debugMode:
            print("CreateWorkArea")
        if debugMode > 1:
            print("screen_width = "+ str(screenWidth))
            print("screen_height = "+ str(screenHeight))

        #try:
        if True:
            # Canvas        
            self.workArea = Canvas(frame, width = screenWidth - 20, height = screenHeight - 80)
            self.workArea.config(bg = "Cornsilk")

            self.x_max = int(self.workArea['width'])
            self.y_max = int(self.workArea['height'])

            if debugMode > 1:
                print("workArea_width = "+ str(self.x_max))
                print("workArea_height = "+ str(self.y_max))
                
            self.x_axis = self.x_max * self.xaxisMarker
            self.y_axis = self.y_max * self.yaxisMarker

            if debugMode > 1:
                print("x axis = "+ str(self.x_axis))
                print("y axis = "+ str(self.y_axis))
                print("x axis marker = "+ str(self.xaxisMarker))
                print("y axis marker = "+ str(self.yaxisMarker))

            coords = [(0, self.invertY(self.y_axis)), (self.x_max, self.invertY(self.y_axis))]
            self.workArea.create_line(coords, fill = "Red", dash=(3, 1))
            coords = [(self.x_axis, self.invertY(0)), (self.x_axis, self.invertY(self.y_max))]
            self.workArea.create_line(coords, fill = "Red", dash=(3, 1))

            self.workArea.grid(row = 1, column = 0, columnspan = 5, padx = wpadx, pady = wpady, sticky = SW)

        #except:
            #print("CreateWorkArea Error")


    def drawToolpath(self, toolpath = []):
        if debugMode: print("VisualiseCode")
        frame = self

        if toolpath: self.toolpath = toolpath
        #else: self.toolpath = []

        if True:
        #if True  
            # refresh workArea to remove any previous visualisation
            self.workArea.delete()
            self.createWorkArea()

            frame.drawButt.configure(state = "disabled")
            frame.zoomInButt.configure(state = "disabled")
            frame.zoomOutButt.configure(state = "disabled")

            self.pause = False
            frame.pauseButt.configure(state = "normal", text = "Pause")

            # set parameters   
            self.pen_colour = "black"
            linetodraw = False
            relative = False
            self.segType = "line"        

            self.currX = self.x_axis
            self.currY = self.y_axis
            self.newx = self.currX
            self.newy = self.currY
            self.I = 0
            self.J = 0

            # process lines in toolpath list
            l_count = 0
            
            for line in self.toolpath:
                l_count += 1
                
                l = []
                cmd = re.findall(r'[^0-9\.\-]+',line) # Extract block command characters
                num = re.findall(r'[0-9\.\-]+',line) # Extract block numbers
                
                if cmd in ['F', 'T', 'M'] : continue
                
                for c in range(len(cmd)) :
                    w = cmd[c] + num[c]
                    l.append(w)
                
                for w in l:
                    if w not in ['G0', 'G1', 'G2', 'G3', 'G90', 'G91'] and w[0] not in ['X', 'Y', 'I', 'J']:
                        continue
                    
                    if w == "G90": relative = False
                    elif w == "G91": relative = True

                    if w == "G0":
                        self.segType = "line"
                        self.pen_colour ="gray"
                    elif w == "G1":
                        self.segType = "line"
                        self.pen_colour = "black"
                    elif w == "G2":
                        self.segType = "arcC"
                        self.pen_colour = "black"
                    elif w == "G3":
                        self.segType = "arcA"
                        self.pen_colour = "black"
                    
                    if w[0] == 'X':
                        if relative:
                            self.newx = self.currX + float(w[1:]) * self.zoom
                            linetodraw = True
                        else:
                            self.newx = self.x_axis + float(w[1:]) * self.zoom
                            linetodraw = True
                            
                    if w[0] == 'Y':
                        if relative:
                            self.newy = self.currY + float(w[1:]) * self.zoom
                            linetodraw = True
                            
                        else:
                            self.newy = self.y_axis + float(w[1:]) * self.zoom
                            linetodraw = True

                    if w[0] == 'I': self.I = float(w[1:]) * self.zoom
                    if w[0] == 'J': self.J = float(w[1:]) * self.zoom
                        
                if linetodraw:
                    while self.pause == True:
                        self.update()
                        time.sleep(0.25)
                        
                    if not self.quickdraw:
                        self.blockText.configure(state = "normal")
                        self.blockText.delete(0.0, END)
                        text2see = str(l_count) + ':  '+ line
                        self.blockText.insert(0.0, text2see)
                        self.blockText.configure(state = "disabled")
                    
                    if self.segType == "line":
                        self.draw_line()

                    elif self.segType[:3] == "arc":
                        if (self.currX == self.newx) and (self.currY == self.newy):
                            self.draw_circle()
                        else:
                            self.draw_arc()
                        
                    self.currX = self.newx
                    self.currY = self.newy
                    posX = self.currX / self.zoom - self.x_axis
                    posY = self.currY / self.zoom  - self.y_axis
                    if debugMode > 1: print("X, Y = " + ' ' + str(posX) + ' ' + str(posY))
                    self.update()
                    linetodraw = False
                    
                    time.sleep(self.speed)

            frame.drawButt.configure(state = "normal")
            frame.pauseButt.configure(state = "disabled")
            if self.zoom < 6: frame.zoomInButt.configure(state = "normal")
            if self.zoom > 1: frame.zoomOutButt.configure(state = "normal")

        #except:
            #print("VisualiseCode Error")

    def setPause(self):
        if debugMode: print("SetPause")

        try:
            self.pause = not self.pause
            if self.pause: self.pauseButt.configure(text = "Continue")
            else: self.pauseButt.configure(text = "Pause")

        except:
            print("SetPause Error")

            
    def doZoom(self, direction):
        if debugMode: print("decZoom")

        #try:
        if True:
            if direction == "out" and self.zoom > 1:
                self.zoom -=1
                ok2zoom = True

            elif direction == "in" and self.zoom < 6:
                self.zoom += 1
                ok2zoom = True

            else:
                ok2zoom = False
            
            if ok2zoom:
                speedMemo = self.speed
                self.speed = 0
                self.quickdraw = True
                self.drawToolpath()
                self.speed = speedMemo
                self.quickdraw = False
                self.update()

        #except:
            #print("doZoom Error")


    def invertY(self, y):
        #if debugMode: print("InvertY")
        try:
            rawY = y
            adjustedY = self.y_max - rawY

        except:
            print("InvertY Error")

        return adjustedY


    def draw_line(self):
        if debugMode > 1: print("Draw_line")
        try:
            x0 = self.currX
            y0 = self.currY
            if debugMode > 1: print("x0, y0 = " + str(x0) + ' ' + str(y0))
            x1 = self.newx
            y1 = self.newy
            if debugMode > 1: print("cX, cY = " + str(x1) + ' ' + str(y1))

            coords = [(x0, self.invertY(y0)), (x1, self.invertY(y1))]
            self.workArea.create_line(coords, fill = self.pen_colour)
        except:
            print ("Draw_line Error")

    def draw_circle(self):
        if debugMode > 1: print("DrawCircle")

        try:
            x0 = self.currX
            y0 = self.currY
            x1 = self.newx
            y1 = self.newy
            I0 = self.I
            J0 = self.J

            cX = x0 + I0
            cY = y0 + J0
            radius = math.sqrt(I0*I0 + J0*J0)
            
            bbox_x0 = cX - radius
            bbox_y0 = cY - radius
            bbox_x1 = cX + radius
            bbox_y1 = cY + radius
            coords = [(bbox_x0, self.invertY(bbox_y0)), (bbox_x1, self.invertY(bbox_y1))]

            self.workArea.create_oval(coords, outline = self.pen_colour)

        except:
            print("DrawCircle Error")

    def draw_arc(self):
        if debugMode > 1: print("DrawArc")

        try:
            x0 = self.currX
            y0 = self.currY
            if debugMode > 1: print("x0, y0 = " + str(x0) + ' ' + str(y0))
            x1 = self.newx
            y1 = self.newy
            if debugMode > 1: print("x1, y1 = " + str(x1) + ' ' + str(y1))
            I0 = self.I
            J0 = self.J
            if debugMode > 1: print("I, J = " + str(I0) + ' ' + str(J0))
            
            cX = x0 + I0
            cY = y0 + J0
            if debugMode > 1: print("cX, cY = " + str(cX) + ' ' + str(cY))
            I1 = cX - x1
            J1 = cY - y1
            if debugMode > 1: print("I1, J1 = " + str(I1) + ' ' + str(J1))

            radius = math.sqrt(I0*I0 + J0*J0)
            
            bbox_x0 = cX - radius
            bbox_y0 = cY - radius
            bbox_x1 = cX + radius
            bbox_y1 = cY + radius

            coords = [(bbox_x0, self.invertY(bbox_y0)), (bbox_x1, self.invertY(bbox_y1))]


            #####
            #
            # START ANG
            #

            # if J == 0 start is on quarter angle 0/360 or 180
            if J0 == 0:

                # if I > 0 start is on quarter angle 180
                if I0 > 0: start_ang = 180

                #if I < 0 start is on quarter angle 0/360
                if I0 < 0: start_ang = 0

            # if J > 0 start is in quadrant 1 or 2 (but flip y for tkinter canvas 1 = 4, 2 = 3)
            elif J0 > 0:

                #if I == 0 start is on quarter angle 90 (but flip y for tkinter 90 = 270)
                #if I0 == 0: start_ang = 90
                if I0 == 0: start_ang = 270

                #else start ang = 90 +/- theta0_deg (but flip y for tkinter 90 = 270)
                else:
                    theta0_rad = math.atan (J0 / I0)
                    theta0_deg = int(theta0_rad * 180 / math.pi)
                    #start_ang = 90 + theta0_deg
                    start_ang = 270 + theta0_deg
                    if debugMode > 1: print("J0>0 Theta0_deg = " + str(theta0_deg))
                    
            # if J < 0 start is in quadrant 3 or 4 (but flip y for tkinter canvas 4 = 1, 3 = 2)
            elif J0 < 0:
                
                #if I == 0 start is on quarter angle 270 (but flip y for tkinter 270 = 90)
                #if I0 == 0: start_ang = 270
                if I0 == 0: start_ang = 90

                #else start ang = 270 +/- theta0_deg  (but flip y for tkinter 270 = 90)
                else:
                    theta0_rad = math.atan (J0 / I0)
                    theta0_deg = int(theta0_rad * 180 / math.pi)
                    #start_ang = 270 + theta0_deg
                    start_ang = 90 + theta0_deg
                    if debugMode > 1: print("J0<0 Theta0_deg = ", theta0_deg)

            if debugMode > 1: print("Start_ang = ", start_ang)


            #####
            #
            # END ANG
            #

            # if J == 0 start is on quarter angle 0/360 or 180
            if J1 == 0:
                
                # if I > 0 start is on quarter angle 180
                if I1 > 0: end_ang = 180

                #if I < 0 start is on quarter angle 0/360
                if I1 < 0: end_ang = 0

            # if J > 0 start is in quadrant 1 or 2(but flip y for tkinter canvas 1 = 4, 2 = 3)
            elif J1 > 0:

                #if I == 0 start is on quarter angle 90 (but flip y for tkinter 90 = 270)
                #if I1 == 0: end_ang = 90
                if I1 == 0: end_ang = 270

                #else start ang = 90 +/- theta0_deg (but flip y for tkinter 90 = 270)
                else:
                    theta1_rad = math.atan (J1 / I1)
                    theta1_deg = int(theta1_rad * 180 / math.pi)
                    #end_ang = 90 + theta1_deg
                    end_ang = 270 + theta1_deg
                    if debugMode > 1: print("J1>0 Theta1_deg = " + str(theta1_deg))
                    
            # if J < 0 start is in quadrant 3 or 4 (but flip y for tkinter canvas 4 = 1, 3 = 2)
            elif J1 < 0:
                
                #if I == 0 start is on quarter angle 270 (but flip y for tkinter 270 = 90)
                #if I1 == 0: end_ang = 270
                if I1 == 0: end_ang = 90

                #else start ang = 270 +/- theta0_deg (but flip y for tkinter 270 = 90)
                else:
                    theta1_rad = math.atan (J1 / I1)
                    theta1_deg = int(theta1_rad * 180 / math.pi)
                    #end_ang = 270 + theta1_deg
                    end_ang = 90 + theta1_deg
                    if debugMode > 1: print("J1<0 Theta1_deg = " + str(theta1_deg))

            if debugMode > 1: print("End_ang = ", str(end_ang))

            # canvas.arc ALWAYS travels anticlock
            # if gcode is anticlock = OK
            # if gcode requires clock need to reverse start and end before drawing
            if self.segType == "arcC":
                temp_ang = start_ang
                start_ang = end_ang
                end_ang = temp_ang
                extent_ang = end_ang - start_ang

            self.workArea.create_arc(coords, outline = self.pen_colour, start = start_ang, extent = extent_ang, style = "arc")

        except:
            print("DrawArc Error")
            


#####
#####
##
## MAIN
##

if __name__ == "__main__":
    root = Tk()

    toolpath =['G17G21G91', '', 'F150', 'G0X30Y20', 'Z-5', 'Z5', 'X60Y20',
               'Z-5', 'Z5', 'X170', 'F150', 'Z-5', 'G2X0Y0I6.5J0', 'G0Z5', 'G0X210',
               'Z-5', 'G2X0Y0I6.5J0', 'G0Z5', 'Y60', 'Z-5', 'G2X0Y0I6.5J0', 'G0Z5',
               'Y170', 'Z-5', 'G2X0Y0I6.5J0', 'G0Z5', 'X60', 'Z-5', 'Z5', 'X30', 'Z-5', 'Z5']
    
    App = Toolpath_VisualiserApp(root, toolpath)
    root.mainloop()
