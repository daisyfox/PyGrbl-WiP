#!/usr/bin/python3.2

"""
Grbl_Python_Controller with Visualiser, gCodeChecker, gCodeEditor

"""

from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfile, askopenfilename, asksaveasfile
import os, sys, glob, serial, time, re

#import os.path
#from copy import *

#import math
#import tkinter.font

from PyGrbl_ScrollTable import *
from PyGrbl_gCodeChecker import *
from PyGrbl_Visualiser import *
from PyGrbl_Control import *


##
# DEGUG MODE SETTING
#

debugMode = 0 # 0=None, 1=High Level Only, 2 = Everything


class Grbl_PyController_GUI(Frame):

    def __init__(self, master, debugMode):
        super(Grbl_PyController_GUI, self).__init__(master)

        self.debugMode = debugMode
        self.gCodeErrors = 0

        mainFont = tkinter.font.nametofont("TkDefaultFont")
        mainFont.configure(size = 10)

        menuFont = tkinter.font.nametofont("TkMenuFont")
        menuFont.configure(size = 10)

        textFont = tkinter.font.nametofont("TkTextFont")
        textFont.configure(size = 12)

        self.screenWidth = 600
        self.screenHeight = 300 - 30 # below Menu and above Status
        self.wpadx = 5
        self.wpady = 5

        self.master.title("Grbl PyController")
        self.master.geometry(str(screenWidth) + "x" + str(screenHeight + 30))

        #self.mainframe = Frame(self)
        self.grid(column = 0, row = 0)

        #self.sysStatus = StringVar()
        #self.sysStatus = "Ok"
       # self.sysStatusLabel = Label(self, textvariable = self.sysStatus)
       # self.sysStatusLabel.grid(row = 1, column = 0, sticky = S)

        self.zoom =defaultZoom
        self.zooming = False
        self.xaxisMarker = defaultXaxisMkr # ratio of axis to be -ve
        self.yaxisMarker = defaultYaxisMkr

        self.filename = ""

        self.gCodeData = []
        self.speed = defaultSpeed

        self.gCodeChecker = Grbl_gCodeChecker(self)
        self.createMenu()

        self.outerFrame = Frame(self)
        self.outerFrame.grid(row = 0, column = 0)
        
        self.createFrames(self.outerFrame)

        #self.createStatusbar(self, 1, 0) # phase IV !
        #self.statusbarText.set("System Status: Ready to Open gCode File OR Connect to GRBL USB Port" )
        
        self.currentFrame = "Control"
        self.menuOptionSelected(self.currentFrame)
        self.update_idletasks()


#####
#####
#
# CREATE GUI MENU, FRAMES & WIDGETS
#
#

    def createMenu(self):
        if self.debugMode > 0:
            status = "Create Menubar"
            print(status)
            #self.statusbarText.set("System Status: " + status)

        self.menubar = Menu(self.master)
        self.master.configure(menu = self.menubar)

        self.filemenu = Menu(self.menubar, tearoff = False)
        self.filemenu.add_command(label = "Open", command = lambda: self.openFile())
        self.filemenu.add_command(label = "Edit", command = lambda: self.todo())
        self.filemenu.add_command(label = "Save", command = lambda: self.todo())
        self.filemenu.add_command(label = "Close", command = lambda: self.todo())
        self.menubar.add_cascade(label = "gCode File", menu = self.filemenu)

        self.gotomenu = Menu(self.menubar, tearoff = False)
        self.gotomenu.add_command(label = "Control", command = lambda: self.menuOptionSelected('Control'))
        self.gotomenu.add_command(label = "gCode Checker", command = lambda: self.menuOptionSelected('gCode Checker'))
        self.gotomenu.add_command(label = "Visualiser", command = lambda: self.menuOptionSelected('Visualiser'))
        self.gotomenu.add_command(label = "Job History", command = lambda: self.menuOptionSelected('Job History'))
        self.menubar.add_cascade(label = "Goto", menu = self.gotomenu)

        self.menubar.add_command(label = "Exit", command = self.onExit)


##    def createStatusbar(self, outerFrame, r, c):
##        self.statusbar = Frame(outerFrame)
##        self.statusbar.grid(row = 1, column = 0, sticky = W+E)
##        
##        self.statusbarText = StringVar()
##        self.statusbarText.set("System Status: ")
##        self.statusbarLabel = Label(self.statusbar, textvariable = self.statusbarText,
##                                            anchor = W, bg = "White")
##        #self.statusbarLabel = Label(self.statusbar, text = "Status Bar: ", anchor = W, bg = "White")
##        self.statusbarLabel.pack(fill = BOTH)


    def createFrames(self, outerFrame):

        frame = outerFrame
        
        if self.debugMode > 0:
            status = "Create Frames"
            print(status)

        #self.controlFrame = Frame(self)
        self.controlFrame = Frame(frame)
        self.create_ControlWidgets()
        self.controlFrame.grid()
        self.controlFrame.grid_forget()

        #self.gCodeCheckerFrame = Frame(self)
        self.gCodeCheckerFrame = Frame(frame)
        self.create_gCodeCheckerWidgets()
        self.gCodeCheckerFrame.grid()
        self.gCodeCheckerFrame.grid_forget()

        #self.visualFrame = Frame(self)
        self.visualFrame = Frame(frame)
        self.create_VisualWidgets()
        self.visualFrame.grid()
        self.visualFrame.grid_forget()

        #self.historyFrame = Frame(self)
        self.historyFrame = Frame(frame)
        self.create_HistoryWidgets()
        self.historyFrame.grid()
        self.historyFrame.grid_forget()


    def create_ControlWidgets(self):
        if self.debugMode > 0:
            status = "Create Control Widgets"
            print(status)
        frame = self.controlFrame
        frame.grid()
        self.controlPanel = Grbl_ControlPanel(frame, self)
        self.controlPanel.grid()


    def create_gCodeCheckerWidgets(self):
        if self.debugMode > 0:
            status = "Create gCode Checker Widgets"
            print(status)
        frame = self.gCodeCheckerFrame
        frame.grid()
        self.gCodeCheckerTable = ScrollTable(frame, self)
        self.gCodeCheckerTable.grid(row = 0, column = 0)

    def create_VisualWidgets(self):
        if self.debugMode > 0:
            status = "Create Visual Widgets"
            print(status)
        frame =self.visualFrame
        frame.grid()
        self.visualiser = Toolpath_Visualiser(frame)
        self.visualiser.grid()

    def create_HistoryWidgets(self):
        if self.debugMode > 0: print("Create History Widgets")
        frame =self.historyFrame

    def setAfter_fileOK(self):
        print("setAfter_fileOK")
        
        if True:
        #try:
            self.gCodeErrors = self.gCodeData[1].count('Error')
            print(self.gCodeErrors)
            if self.gCodeErrors > 0:
                self.filename = "Current Job: " + self.shortname + ' has ' + str(self.gCodeErrors) + ' errors'
                self.controlPanel.setWCstate(self.controlPanel.jobmgr, "cmdButton", "disabled")
                temp_opt = "gCode Checker"
            else:
                self.filename = "Current Job: " + self.shortname
                if self.controlPanel.usbConn["text"] == "Disconnect":
                    self.controlPanel.setWCstate(self.controlPanel.jobmgr, "cmdButton", "normal")
                temp_opt = "Control"
                self.controlPanel.gCodeData = []
                toolpath = []
                for l in self.gCodeData[3]:
                    if l is not '':
                        self.controlPanel.gCodeData.append(l)
                        toolpath.append(l)

            self.controlPanel.jobmgrLabelVar.set(self.filename)
            self.gCodeCheckerTable.fill_STable(self.gCodeData)
            self.visualiser.drawToolpath(toolpath)
            self.menuOptionSelected(temp_opt)
            self.update_idletasks()

    def setAfter_connect(self):
        print("setAfter_connect")

    def reset_ControlWidgets(self, resetType):
        print("reset Control Widgets")
        
        # Widget of type Widget Class
        #self.controlPanel.setWCstate(self.controlPanel.jobmgr, "cmdButton", "normal")

        # Specific Widget
        # self.controlPanel.setWstate(self.controlPanel.widget, "normal")

        if resetType == 'newFile':
            self.controlPanel.setWCstate(self.controlPanel.jobmgr, 'cmdButton', 'disabled')


    def reset_gCodeCheckerWidgets(self, resetType):
        print("reset gCodeChecker Widgets")

    def reset_VisualWidgets(self, resetType):
        print("reset Visual Widgets")

    def newFileReset(self):
        print("New File Reset")
        
        self.reset_gCodeCheckerWidgets('newFile')

    def restart(self):
        print("restart")
        self.reset_ControlWidgets('all', 'disabled')
        self.reset_gCodeCheckerWidgets('all', 'disabled')
        self.reset_VisualWidgets('all', 'disabled')


#####
#####
#
# NAVIGATION
#
#

    def todo(self):
        #default command during development
        pass

    def onExit(self):
        if self.debugMode > 0: print("on Exit")
        self.master.destroy()

    def menuOptionSelected(self, optionLabel):
        if self.debugMode > 0: print("Menu Option Selected: " + optionLabel)

        if self.currentFrame == "Control": self.controlFrame.grid_remove()
        elif self.currentFrame == "gCode Checker": self.gCodeCheckerFrame.grid_remove()
        elif self.currentFrame == "Visualiser": self.visualFrame.grid_remove()
        elif self.currentFrame == "Job History": self.historyFrame.grid_remove()

        if optionLabel == "Control":
            self.controlFrame.grid()

        elif optionLabel == "gCode Checker":
            self.gCodeCheckerFrame.grid()
            self.update_idletasks()
            self.gCodeCheckerTable.canvas.configure(scrollregion = self.gCodeCheckerTable.canvas.bbox('all'))

        elif optionLabel == "Visualiser":
            self.visualFrame.grid()
            self.update_idletasks()
            
        elif optionLabel == "Job History":
            self.historyFrame.grid()

        self.currentFrame = optionLabel
        self.update_idletasks()


    def openFile(self):
        if debugMode > 0: print("OpenFile")

        self.newFileReset()
        
        self.gCodeFile = askopenfilename()
        if debugMode > 1: print(self.gCodeFile)

        if self.gCodeFile:
            self.shortname =os.path.split(self.gCodeFile)[1]
            #self.fileLabelVar.set("Filename: " + self.shortname)
            if debugMode > 1: print("File shortname: ", self.shortname)
            
            self.gCodeData = []
            self.gCodeData = self.gCodeChecker.check(self.gCodeFile)
            if debugMode > 1: print(self.gCodeData)

            self.setAfter_fileOK()


#####
#####
##
## MAIN
##

if __name__ == "__main__":
    root = Tk()

    visualiser = Grbl_PyController_GUI(root, debugMode)
    root.mainloop()
