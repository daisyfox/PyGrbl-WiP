#!/usr/bin/python2.7

import cwiid, time
from Tkinter import *
from tkMessageBox import *

import pyautogui

class PyGrbl_GUI(Frame, object):
    def __init__(self, master):
        super(PyGrbl_GUI, self).__init__(master)

        ##  WHO AM I ?
        #print("Who am I: " + self.winfo_class())  # = 'Frame' !!
        #print("Who am I: " + self.__class__.__name__) # = 'PyGrbl_GUI'

        self.master.protocol("WM_DELETE_WINDOW", self.onExit)

        #--------------------------------------------------------------------
        # APPLICATION WIDE VARIABLES
        #--------------------------------------------------------------------

        self.debugMode = 1 # 0=None, 1=Exit procedures OK/Error, 2 = Everything

        #  apps running
        self.apps = [] # list of apps for goto menu & knowing what  is running
        self.currentApp = ""

##        self.bind_all('<Enter>', lambda event : self.enterWidget(event))

        #--------------------------------------------------------------------
        # GUI SETUP
        #--------------------------------------------------------------------
        self.screenWidth = 890
        self.screenHeight = 460 # below Menu and above Status
        self.master.geometry(str(self.screenWidth) + "x" + str(self.screenHeight - 30))
        self.grid(column = 0, row = 0)

        self.createMenu()
        self.mainFrame = Frame(self)
        self.mainFrame.grid(row = 0, column = 0)

        self.wii = PyGrbl_Wii(self, self)

        self.update_idletasks()


    #--------------------------------------------------------------------
    # CREATE GUI MAIN WINDOW, MENU & STATUS BAR
    #--------------------------------------------------------------------
    def createMenu(self):
        try:
            self.menubar = Menu(self.master)
            self.master.configure(menu = self.menubar)

            self.wiimenu = Menu(self.menubar, tearoff = False)
            self.wiimenu.add_command(label = "Connect", command = lambda: self.wii.wiiConnect())
            self.wiimenu.add_command(label = "Disconnect", state = "disabled", command = lambda: self.wii.wiiStop())
            self.menubar.add_cascade(label = "WiiMote", menu = self.wiimenu)

            if self.debugMode > 0:
                print("CreateMenu: Ok")

        except:
            if self.debugMode > 0:
                print("CreateMenu: Error")
                

    #--------------------------------------------------------------------
    # NAVIGATION
    #--------------------------------------------------------------------
    def todo(self):
        #default command during development
        pass

    def onExit(self):
        try:
            if askokcancel("Just Checking", "Do you want to close now?"):
                if self.wii.wiiState == "Connected": self.wii.wiiStop()
                self.master.destroy()

            if self.debugMode > 0: print("on Exit: Ok")

        except:
            if self.debugMode > 0:
                print("on Exit: Error")


#-------------------------------------------------
# PyGrbl_Wii
#-------------------------------------------------
class PyGrbl_Wii(Frame):
    def __init__(self, master, app):
        Frame.__init__(self, master = master)

        ##  WHO AM I ?
        #print(self.winfo_class())  # = 'Frame' !!
        #print(self.__class__.__name__) # = 'PyGrbl_Wii'

        self.app = app
        self.wiiState = "Disconnected"

    def wiiConnect(self):
        if True:
            mess = "Connecting to your Wiimote. Make sure you are holding buttons 1 + 2!"
            showinfo(title="WiiMote Connection", message = mess)
            self.wiiState = self.wiiStart()
            while self.wiiState == "Retry":
                self.wiiState = self.wiiStart()
            if self.wiiState == "Connected":
                if self.app.debugMode > 0: print("wiiConnect: Ok")
                self.readWiiButtonsA()

        #except:
            #if self.app.debugMode > 0: print("wiiConnect: Error")

    def wiiStart(self):
        try:
            try:
                self.wii=cwiid.Wiimote("CC:9E:00:CD:96:FC")
                self.wii.rumble = 1
                time.sleep(0.25)
                self.wii.rumble = 0
                self.wii.led = 1
                self.app.wiimenu.entryconfig("Connect", state = "disabled")
                self.app.wiimenu.entryconfig("Disconnect", state = "normal")
                if self.app.debugMode > 1: print("wiiStart (conn): Ok")
                result = "Connected"
            except:
                mess = "Cannot connect to your Wiimote. Run again and make sure you are holding buttons 1 + 2!"
                if askretrycancel(title="WiiMote Connection", message = mess):
                    if self.app.debugMode > 1: print("wiiStart (retry): Ok")
                    result = "Retry"
                else:
                    if self.app.debugMode > 1: print("wiiStart (disconn): Ok")
                    result = "Disconnected"

            return result

        except:
           if self.app.debugMode > 1: print("wiiStart: Error")

    def wiiStop(self):
        try:
            self.wii.rumble = 1
            time.sleep(0.25)
            self.wii.rumble = 0
            self.wii.close()
            self.app.wiimenu.entryconfig("Connect", state = "normal")
            self.app.wiimenu.entryconfig("Disconnect", state = "disabled")

            if self.app.debugMode > 1: print("wiiStop: Ok")

            return "Disconnected"

        except:
            if self.app.debugMode > 1: print("wiiStop: Error")

    def readWiiButtons(self):
        try:
            if self.wiiState == "Connected":
                try:
                    # check that singal not lost
                    self.wii.rpt_mode = cwiid.RPT_BTN
                except:
                    self.wiiState = "Disconnected" # if signal lost, update wiiState
                    return

                buttons = self.wii.state['buttons']
                if buttons:
                    if (buttons - cwiid.BTN_LEFT == 0): print('Jog X-')
                    elif(buttons - cwiid.BTN_RIGHT == 0): print('Jog X+')
                    elif (buttons - cwiid.BTN_UP == 0): print('Jog Y+')
                    elif (buttons - cwiid.BTN_DOWN == 0): print('Jog Y-')
                    elif (buttons  - (cwiid.BTN_B + cwiid.BTN_UP) == 0): print('Jog Z+')
                    elif (buttons - (cwiid.BTN_B + cwiid.BTN_DOWN) == 0): print('Jog Z-')
                    elif (buttons - cwiid.BTN_1 == 0): print 'Button 1 pressed'
                    elif (buttons - cwiid.BTN_2 == 0): print 'Button 2 pressed'
                    elif (buttons - cwiid.BTN_A == 0): print 'Button A pressed'
                    elif (buttons & cwiid.BTN_MINUS): print 'Minus Button pressed'
                    elif (buttons & cwiid.BTN_PLUS): print 'Plus Button pressed'

                self.after(50, self.readWiiButtons)

            if self.app.debugMode > 2: print("readWiiButtons: Ok")

        except:
            if self.app.debugMode > 1: print("readWiiButtons: Error")




    def readAcc(self):
        self.wii.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
        wiiX = self.wii.state['acc'][cwiid.X] # '-' < 120, '+' > 120
        wiiY = self.wii.state['acc'][cwiid.Y]
        print(wiiX, wiiY)
        if wiiX+wiiY != 0:
            pyautogui.moveRel(wiiX - 120, wiiY - 120)

        try:
            check = (self.wii.state['buttons'] - cwiid.BTN_HOME)
            if check == 0: # home button still pressed
                self.after(20, self.readAcc)
            else:
                self.after(50, self.readWiiButtonsA)

        except:
            print("readAcc: Error") # probably caused by lost connection

    def readOther(self):
        buttons = self.wiiButtons

        if (buttons - cwiid.BTN_LEFT == 0): print('Jog X-')
        elif(buttons - cwiid.BTN_RIGHT == 0): print('Jog X+')
        elif (buttons - cwiid.BTN_UP == 0): print('Jog Y+')
        elif (buttons - cwiid.BTN_DOWN == 0): print('Jog Y-')
        elif (buttons  - (cwiid.BTN_B + cwiid.BTN_UP) == 0): print('Jog Z+')
        elif (buttons - (cwiid.BTN_B + cwiid.BTN_DOWN) == 0): print('Jog Z-')
        elif (buttons - cwiid.BTN_1 == 0): print 'Button 1 pressed'
        elif (buttons - cwiid.BTN_2 == 0): print 'Button 2 pressed'
        elif (buttons - cwiid.BTN_A == 0): print 'Button A pressed'
        elif (buttons & cwiid.BTN_MINUS): print 'Minus Button pressed'
        elif (buttons & cwiid.BTN_PLUS): print 'Plus Button pressed'

        self.after(50, self.readWiiButtonsA)


    def readWiiButtonsA(self):
        if True:
            if self.wiiState == "Connected": # wiiState indicates 'connected'
                try:
                    self.wii.rpt_mode = cwiid.RPT_BTN # check that signal not lost
                except:
                    self.wiiState = "Disconnected" # if signal lost, update wiiState
                    return

                #self.wiiBatt = self.wii.state['battery'] # TO DO: put this somewhere more suitable

                self.wiiButtons = self.wii.state['buttons']
                if self.wiiButtons:
                    if self.wiiButtons & cwiid.BTN_HOME:
                        self.readAcc()
                        self.wii.rpt_mode = cwiid.RPT_BTN

                    else:
                        self.readOther()

                else: # if no buttons pressed - try again later !
                    self.after(50, self.readWiiButtonsA)


            if self.app.debugMode > 2: print("readWiiButtons: Ok")
        #except:
            #if self.app.debugMode > 1: print("readWiiButtons: Error")




#-------------------------------------------------
# MAIN
#-------------------------------------------------

if __name__ == "__main__":
    root = Tk()

    app = PyGrbl_GUI(root)
    wii = PyGrbl_Wii(app, app.mainFrame)

    app.master.title("PyGrbl Wiimote")
    
    root.mainloop()
