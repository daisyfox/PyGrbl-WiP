#!/usr/bin/python2.7

"""
Toolpath_Visualiser

"""

from Tkinter import *
#from tkinter import ttk

#import time, re

#import math
#import tkinter.font

from PyGrbl_GUI import *
from PyGrbl_gCodeChecker import *

class PyGrbl_Visualiser(Frame):    
    def __init__(self, master, app):
        Frame.__init__(self, master = master)

        ##  WHO AM I ?
        #print("Who am I:  " + self.winfo_class())  # = 'Frame' !!
        #print("Who is my parent: " + app.__class__.__name__) # = PyGrbl_GUI
        #print("Who am I:  " + self.__class__.__name__) # = 'PyGrbl_Visualiser'
        
        self.app = app
        self.app.servicemenu.entryconfig("Visualiser", state = "normal")
        self.app.apps.append(self.__class__.__name__)
        self.openFileTrace = self.app.fileOpenFlag.trace_variable('w', self.fileOpenTraceAction)

        self.screenWidth = self.master.winfo_width() - 50
        self.screenHeight = self.master.winfo_height() - 50
        self.defaultXaxisMkr = 0.05 # % X in -ve
        self.defaultYaxisMkr = 0.95 # % Y in -ve
        self.defaultZoom = 1
        self.defaultSpeed = 0.1 # delay (sec) when drawing toolpath

        self.toolpath = []
        self.zoom = self.defaultZoom
        self.zooming = False
        self.xaxisMarker = self.defaultXaxisMkr # ratio of axis to be -ve
        self.yaxisMarker = self.defaultYaxisMkr
        self.speed = self.defaultSpeed
        self.quickdraw = False

        self.createVisualWidgets()
        
        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)
        self.grid(column = 0, row = 0, sticky = (N, S, W, E))


    def createVisualWidgets(self):
        r = 0
        c = 0
        # Buttons
        self.drawButt = visButton(self, self, "Draw", "draw", r, c)
        self.pauseButt = visButton(self, self, "Pause", "pause", r, c + 2)
        self.zoomInButt = visButton(self, self, "Zoom In", "zoomin", r, c + 3)
        self.zoomOutButt = visButton(self, self, "Zoom Out", "zoomout", r, c + 4)

        # gCode Block Text
        self.blockText = Text(self, width = 30, height = 1, font = (14), highlightcolor = "white", state = "disabled")
        self.blockText.grid(row = r, column = c + 1, padx = 5, pady = 5, sticky = W)

        self.createWorkArea()

        for col in range(5):
            self.columnconfigure(col, weight = 1)
        self.rowconfigure(1, weight = 1)
        

    def createWorkArea(self):        
        try:
            # Canvas
            self.workAreaF = Frame(self)
            self.workAreaF.grid(row = 1, column = 0, columnspan = 5, padx = 5, pady = 5, sticky = (N, S, W, E))
            self.workArea = Canvas(self.workAreaF, width = self.screenWidth, height = self.screenHeight)
            self.workArea.config(bg = "Cornsilk")

            self.x_max = int(self.workArea['width'])
            self.y_max = int(self.workArea['height'])
                
            self.x_axis = self.x_max * self.xaxisMarker
            self.y_axis = self.y_max * self.yaxisMarker

            coords = [(0, self.invertY(self.y_axis)), (self.x_max, self.invertY(self.y_axis))]
            self.workArea.create_line(coords, fill = "Red", dash=(3, 1))
            coords = [(self.x_axis, self.invertY(0)), (self.x_axis, self.invertY(self.y_max))]
            self.workArea.create_line(coords, fill = "Red", dash=(3, 1))

            #self.workArea.grid(row = 1, column = 0, columnspan = 5, padx = 5, pady = 5, sticky = (N, S, W, E))
            self.workArea.pack(fill = BOTH, expand = YES)
            self.update_idletasks()

            self.bind("<Configure>", self.on_resize)

            if self.app.debugMode > 1: print("CreateWorkArea: Ok")

        except:
            print("CreateWorkArea: Error")

    def fileOpenTraceAction(self, name, index, mode):
        try:
            if self.app.fileOpenFlag.get() == True:
                self.drawButt.configure(state = "normal")
                
            elif self.app.fileOpenFlag.get() == False:
                for child in self.winfo_children():
                        if child.__class__.__name__ in "visButton":
                            child.configure(state = "disabled")

                self.workArea.delete() # reset workArea to remove previous visualisation
                self.createWorkArea()
                self.zoom = self.defaultZoom
                self.blockText.configure(state = "normal")
                self.blockText.delete(0.0, END)
                self.blockText.configure(state = "disabled")

            if self.app.debugMode > 1: print("fileOpenTraceAction: Ok")

        except:
            print("fileOpenTraceAction: Error")

    def visButtonHandler(self, request):
        if self.app.debugMode > 1: print("Button Handler")

        if request == 'draw': self.drawToolpath()
        elif request == 'pause': self.setPause()
        elif request == 'zoomin': self.doZoom('in')
        elif request == 'zoomout': self.doZoom('out')

    def on_resize(self, event):
        itemcount = len(self.workArea.find_all()) - 2
        self.screenWidth = self.master.winfo_width() - 50
        self.screenHeight = self.master.winfo_height() - 50
        self.workArea.delete()
        self.createWorkArea()

        if itemcount > 0:
            speedMemo = self.speed
            self.speed = 0
            self.quickdraw = True
            self.drawToolpath()
            self.speed = speedMemo
            self.quickdraw = False
            self.update()

    def drawToolpath(self):
        if True:
#        try:
            if self.app.gCodeData[2] == []:
                if self.toolpath == []:
                    for line in self.app.inFile:
                        block = re.sub('\s|\(.*?\)','',line).upper() 
                        block = re.sub('\\\\','',block) # Strip \ block delete character
                        block = re.sub('%','',block) # Strip % program start/stop character
                        self.toolpath.append(block)
            else:
                self.toolpath = self.app.gCodeData[3]

            self.workArea.delete() # refresh workArea to remove previous visualisation
            self.createWorkArea()

            self.drawButt.configure(state = "disabled")
            self.zoomInButt.configure(state = "disabled")
            self.zoomOutButt.configure(state = "disabled")

            self.pause = False
            self.pauseButt.configure(state = "normal", text = "Pause")

            # set parameters   
            self.pen_colour = "black"
            linetodraw = False
            relative = False
            self.segType = "line"        

            self.currX = self.x_axis
            self.currY = self.y_axis
            self.newX = self.currX
            self.newY = self.currY
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
                    if w in ['G0', 'G1', 'G2', 'G3', 'G90', 'G91'] or w[0] in ['X', 'Y', 'I', 'J']:
                        if w == "G90": relative = False
                        elif w == "G91": relative = True

                        if w == "G0": self.segType = "line"
                        elif w == "G1": self.segType = "line"
                        elif w == "G2": self.segType = "arcC"
                        elif w == "G3": self.segType = "arcA"

                        if w == "G0": self.pen_colour ="gray"
                        elif w in ["G1", "G2", "G3"]: self.pen_colour = "black"

                        if w[0] in ['X', 'Y']:
                            linetodraw = True
                            if w[0] == 'X':
                                if relative: self.newX = self.currX + float(w[1:]) * self.zoom
                                else: self.newX = self.x_axis + float(w[1:]) * self.zoom
             
                            elif w[0] == 'Y':
                                if relative: self.newY = self.currY + float(w[1:]) * self.zoom
                                else: self.newY = self.y_axis + float(w[1:]) * self.zoom

                        elif w[0] == 'I': self.I = float(w[1:]) * self.zoom
                        elif w[0] == 'J': self.J = float(w[1:]) * self.zoom
                        
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
                        self.draw_line(self.currX, self.currY, self.newX, self.newY)

                    elif self.segType[:3] == "arc":
                        if (self.currX == self.newX) and (self.currY == self.newY):
                            self.draw_circle()
                        else:
                            self.draw_arc()
                        
                    self.currX = self.newX
                    self.currY = self.newY
                    posX = self.currX / self.zoom - self.x_axis
                    posY = self.currY / self.zoom  - self.y_axis
                    self.update()
                    linetodraw = False
                    
                    time.sleep(self.speed)

            self.drawButt.configure(state = "normal")
            self.pauseButt.configure(state = "disabled")
            if self.zoom < 6: self.zoomInButt.configure(state = "normal")
            if self.zoom > 1: self.zoomOutButt.configure(state = "normal")

            if self.app.debugMode > 1: print("Draw Toolpath: Ok")

#        except:
 #           print("Draw Toolpath: Error")

    def setPause(self):
        try:
            self.pause = not self.pause
            if self.pause: self.pauseButt.configure(text = "Continue")
            else: self.pauseButt.configure(text = "Pause")
            
            if self.app.debugMode > 1: print("SetPause: Ok")

        except:
            if self.app.debugMode > 1: print("SetPause: Error")

            
    def doZoom(self, direction):
        try:
            ok2zoom = False
            if direction == "out" and self.zoom > 1:
                self.zoom -=1
                ok2zoom = True

            elif direction == "in" and self.zoom < 6:
                self.zoom += 1
                ok2zoom = True
            
            if ok2zoom:
                speedMemo = self.speed
                self.speed = 0
                self.quickdraw = True
                self.drawToolpath()
                self.speed = speedMemo
                self.quickdraw = False
                self.update()
                
            if self.app.debugMode > 1: print("doZoom: Ok")

        except:
            if self.app.debugMode > 1: print("doZoom Error")


    def invertY(self, y):
        try:
            rawY = y
            adjustedY = self.y_max - rawY

        except:
            if self.app.debugMode > 1: print("InvertY Error")

        return adjustedY


    def draw_line(self, startX, startY, endX, endY):
        try:
            coords = [(startX, self.invertY(startY)), (endX, self.invertY(endY))]
            self.workArea.create_line(coords, fill = self.pen_colour)

            if self.app.debugMode > 1: print("Draw_line: Ok")

        except:
            if self.app.debugMode > 1: print ("Draw_line: Error")

    def draw_circle(self):
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
            
            if self.app.debugMode > 1: print("DrawCircle: Ok")

        except:
            if self.app.debugMode > 1: print("DrawCircle Error")

    def draw_arc(self):
        try:
            x0 = self.currX
            y0 = self.currY
            x1 = self.newx
            y1 = self.newy
            I0 = self.I
            J0 = self.J
            
            cX = x0 + I0
            cY = y0 + J0
            I1 = cX - x1
            J1 = cY - y1

            radius = math.sqrt(I0*I0 + J0*J0)
            
            bbox_x0 = cX - radius
            bbox_y0 = cY - radius
            bbox_x1 = cX + radius
            bbox_y1 = cY + radius

            coords = [(bbox_x0, self.invertY(bbox_y0)), (bbox_x1, self.invertY(bbox_y1))]

            #----------------------------------------
            # START ANG
            #----------------------------------------
            if J0 == 0: # start is on quarter angle 0/360 or 180
                if I0 > 0: start_ang = 180 # start is on quarter angle 180
                if I0 < 0: start_ang = 0 #start is on quarter angle 0/360

            elif J0 > 0:# start is in quadrant 1 or 2 (but flip y for tkinter canvas 1 = 4, 2 = 3)
                if I0 == 0: start_ang = 270 #start is on quarter angle 90 (but flip y for tkinter 90 = 270)

                else: # start ang = 90 +/- theta0_deg (but flip y for tkinter 90 = 270)
                    theta0_rad = math.atan (J0 / I0)
                    theta0_deg = int(theta0_rad * 180 / math.pi)
                    start_ang = 270 + theta0_deg
                    if self.app.debugMode > 1: print("J0>0 Theta0_deg = " + str(theta0_deg))
            
            elif J0 < 0: # start is in quadrant 3 or 4 (but flip y for tkinter canvas 4 = 1, 3 = 2)
                if I0 == 0: start_ang = 90 # start is on quarter angle 270 (but flip y for tkinter 270 = 90)
                
                else: # start ang = 270 +/- theta0_deg  (but flip y for tkinter 270 = 90)
                    theta0_rad = math.atan (J0 / I0)
                    theta0_deg = int(theta0_rad * 180 / math.pi)
                    start_ang = 90 + theta0_deg
                    if self.app.debugMode > 1: print("J0<0 Theta0_deg = ", theta0_deg)

            if self.app.debugMode > 1: print("Start_ang = ", start_ang)

            #----------------------------------------
            # END ANG
            #----------------------------------------
            if J1 == 0: # start is on quarter angle 0/360 or 180
                if I1 > 0: end_ang = 180 # start is on quarter angle 180
                if I1 < 0: end_ang = 0 # start is on quarter angle 0/360

            elif J1 > 0: # start is in quadrant 1 or 2(but flip y for tkinter canvas 1 = 4, 2 = 3)
                if I1 == 0: end_ang = 270 # start is on quarter angle 90 (but flip y for tkinter 90 = 270)

                else: # start ang = 90 +/- theta0_deg (but flip y for tkinter 90 = 270)
                    theta1_rad = math.atan (J1 / I1)
                    theta1_deg = int(theta1_rad * 180 / math.pi)
                    end_ang = 270 + theta1_deg
                    if self.app.debugMode > 1: print("J1>0 Theta1_deg = " + str(theta1_deg))

            elif J1 < 0: # start is in quadrant 3 or 4 (but flip y for tkinter canvas 4 = 1, 3 = 2)
                if I1 == 0: end_ang = 90 # start is on quarter angle 270 (but flip y for tkinter 270 = 90)

                else: # start ang = 270 +/- theta0_deg (but flip y for tkinter 270 = 90)
                    theta1_rad = math.atan (J1 / I1)
                    theta1_deg = int(theta1_rad * 180 / math.pi)
                    end_ang = 90 + theta1_deg
                    if self.app.debugMode > 1: print("J1<0 Theta1_deg = " + str(theta1_deg))

            if self.app.debugMode > 1: print("End_ang = ", str(end_ang))

            # canvas.arc ALWAYS travels anticlock, if gcode 'clock' reverse start and end
            if self.segType == "arcC":
                temp_ang = start_ang
                start_ang = end_ang
                end_ang = temp_ang
                extent_ang = end_ang - start_ang

            self.workArea.create_arc(coords, outline = self.pen_colour, start = start_ang, extent = extent_ang, style = "arc")

            if self.app.debugMode > 1: print("DrawArc: Ok")

        except:
            if self.app.debugMode > 1: print("DrawArc: Error")

            
class visButton(Button):
    def __init__(self, master, mainClass, btext, action, r, c):
        Button.__init__(self, master = master)

        self.configure(text = btext, command = lambda: mainClass.visButtonHandler(action))
        self.configure(width = 6, state = "disabled")
        self.grid(row = r, column = c, padx = 5, pady = 2, sticky = W)


#####
#####
##
## MAIN
##

if __name__ == "__main__":
    root = Tk()

    app = PyGrbl_GUI(root)
    app.master.title("PyGrbl Visualiser")

    app.Visualiser = PyGrbl_Visualiser(app.mainFrame, app)
    app.currentApp = app.Visualiser
    
    root.mainloop()
