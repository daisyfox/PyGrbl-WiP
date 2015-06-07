#!/usr/bin/python3.2

"""
PyGrbl App Class

"""

from Tkinter import *
#from tkinter import ttk

#from tkinter.filedialog import askopenfilename, asksaveasfile

class PyGrbl_App(Frame, object):
    def __init__(self, master):
        super(PyGrbl_App, self).__init__(master)

        #--------------------------------------------------------------------
        # GLOBAL VARIABLES
        #--------------------------------------------------------------------

        self.debugMode = 1 # 0=None, 1=Exit procedures OK/Error, 2 = Everything

        #  apps running
        self.apps = ["PyGrbl_App_Window"] # need to know which apps active for 'goto' menu

        # status flags
        self.gCodeErrors = 0

        # shared variables / data
        self.filename = ""
        self.gCodeData = []

        #--------------------------------------------------------------------
        # GUI SETUP
        #--------------------------------------------------------------------
        self.screenWidth = 890
        self.screenHeight = 460 # below Menu and above Status
        self.master.title("PyGrbl v 0.2 (dev)")
        self.master.geometry(str(self.screenWidth) + "x" + str(self.screenHeight - 30))
        self.grid(column = 0, row = 0)

        self.createMenu()
        self.mainFrame = Frame(self)
        self.mainFrame.grid(row = 0, column = 0)

        #self.wii = wiiHandler(self.mainFrame)
        self.bind("<Key>", self.key)

        self.createStatusbar(self, 1, 0)

        self.focus_force()
        self.update_idletasks()


    #--------------------------------------------------------------------
    # CREATE GUI MAIN WINDOW, MENU & STATUS BAR
    #--------------------------------------------------------------------

    def createMenu(self):
        try:
            self.menubar = Menu(self.master)
            self.master.configure(menu = self.menubar)

            self.filemenu = Menu(self.menubar, tearoff = False)
            self.filemenu.add_command(label = "Open", command = lambda: self.openFile())
            self.filemenu.add_command(label = "Save", command = lambda: self.todo())
            self.filemenu.add_command(label = "Close", command = lambda: self.todo())
            self.menubar.add_cascade(label = "gCode File", menu = self.filemenu)

            self.menubar.add_command(label = "Exit", command = self.onExit)

            if self.debugMode > 0:
                print("CreateMenu: Ok")

        except:
            if self.debugMode > 0:
                print("CreateMenu: Error")


    def createStatusbar(self, outerFrame, r, c):
        try:
            self.statusbar = Frame(outerFrame)
            self.statusbar.grid(row = r, column = c, sticky = W+E)

            self.statusbarText = StringVar()
            self.statusbarText.set("System Status: ")
            self.statusbarLabel = Label(self.statusbar, textvariable = self.statusbarText,
                                                anchor = W, bg = "White")
            self.statusbarLabel = Label(self.statusbar, text = "Status Bar: ", anchor = W, bg = "White")
            self.statusbarLabel.pack(fill = BOTH)

            if self.debugMode > 0:
                print("CreateStatusbar: Ok")

        except:
            if self.debugMode > 0:
                print("CreateStatusbar: Error")


    #----------------------------------------------------------------------
    # ADD PyGrbl App to Main Window, add Menu options
    #----------------------------------------------------------------------

    def addApp(self, appName):
        try:
            pass
        
            if self.debugMode > 0:
                print("AddApp " + appName + ": Ok")

        except:
            if self.debugMode > 0:
                print("AddApp " + appName + ": Error")

#------------------------------------------------------------------------------------
#       Wii Remote Buttons
#------------------------------------------------------------------------------------

    def key(self, event):
        #print "Key pressed:  ", event.keycode, "   Key state: ", event.state
        key_pressed = event.keycode
        key_state = event.state
        
# A         = KEY_A (38)
# B         = KEY_B (50 - but used as state modifier (state = 1))
# Up       = KEY_UP (111)
# Down	= KEY_DOWN (116)
# Left	= KEY_LEFT (113)
# Right	= KEY_RIGHT (114)
# Minus	= KEY_BACK (166)
# Plus	= KEY_FORWARD (167)
# Home	= KEY_HOME (110)
# 1	= KEY_1 (10)
# 2	= KEY_2 (11)

        if key_pressed == 38: print("A")
        elif key_pressed == 50: print("B")
        elif key_pressed == 113: print("LEFT")
        elif key_pressed == 114: print("RIGHT")
        elif key_pressed == 166: print("MINUS")
        elif key_pressed == 167: print("PLUS")
        elif key_pressed == 110: print("HOME")
        elif key_pressed == 10: print("1")
        elif key_pressed == 11: print("2")

        elif key_pressed == 111:
            if event.state == 0: print("UP")
            else: print("B&UP")
        elif key_pressed == 116:
            if event.state == 0: print("DOWN")
            else: print("B&DOWN")


    #--------------------------------------------------------------------
    # NAVIGATION
    #--------------------------------------------------------------------

    def todo(self):
        #default command during development
        pass

    def onExit(self):
        try:
            self.master.destroy()

            if self.debugMode > 0:
                print("on Exit: Ok")

        except:
            if self.debugMode > 0:
                print("on Exit: Error")


    def menuOptionSelected(self, optionLabel):
        try:
            # trigger event to hide current frame
            # set global variable current frame to new optionLabel
            # trigger event to show new current frame

            self.currentFrame = optionLabel
            self.update_idletasks()

            if self.debugMode > 0:
                print("Menu Option Selected: " + optionLabel + ": Ok")

        except:
            if self.debugMode > 0:
                print("Menu Option Selected: Error")


#-------------------------------------------------
# gCODE FILE MENU
#-------------------------------------------------

    def openFile(self):
        try:
##            self.gCodeFile = askopenfilename()
##
##            if self.gCodeFile:
##                self.fileShortname =os.path.split(self.gCodeFile)[1]
##                self.inFile = open(file, 'r') # change to ''w' for Editor work ?
##
##            self.fileOpenFlag = True

            if debugMode > 0:
                print("OpenFile: Ok")

        except:
            if self.debugMode > 0:
                print("OpenFile: Error")

    def saveFile(self):
        try:
            pass

            if debugMode > 0:
                print("saveFile: Ok")

        except:
            if self.debugMode > 0:
                print("saveFile: Error")


    def closeFile(self):
        try:
            self.inFile.close()
            #pop up dialog - close without saving?
            self.fileOpenFlag = False

            if debugMode > 0:
                print("closeFile: Ok")

        except:
            if self.debugMode > 0:
               print("closeFile: Error")



class myButton(Button):
    def __init__(self, master, btext, r, c):
        Button.__init__(self, master = master)

        self.configure(text = btext)
        self.configure(state = "disabled")
        self.grid(row = r, column = c)


#-------------------------------------------------
# MAIN
#-------------------------------------------------

if __name__ == "__main__":
    root = Tk()

    app = PyGrbl_App(root)

    #add PyGrbl_gCodeChecker
    #add PyGrbl_ControlPanel
    #add PyGrbl_Visualiser
    #add PyGrbl_Editor
    
    root.mainloop()
