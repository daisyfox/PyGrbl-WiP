#!/usr/bin/python3.2

"""
PyGrbl App Class

"""

from Tkinter import *

from PyGrbl_App import PyGrbl_App


class Control_Panel(Frame):
    def __init__(self, master):
        Frame.__init__(self, master = master)

        self.master = master

        try:
            self.debugMode = self.master.debugMode
            
        except:
            self.debugMode = 1
            print("debug Exception: Grbl_ControlPanel")
            
        if self.debugMode > 0: print("init Grbl ControlPanel")

        self.create_ControlWidgets()


    def create_ControlWidgets(self):

        ## LEFTSIDE CONTROLS
        
        # USB CONNECTION MANAGER
        self.usbmgr = Frame(self, borderwidth = 2, relief = RIDGE)
        self.usbmgrLabel = Label(self.usbmgr, text = "USB Port")
        self.usbmgrLabel.grid(row = 0, column = 0, sticky = (S, W))

        # usb combobox list
        usbPorts = ['usbports']
        ports = ('a', 'b', 'c')
        for p in ports: usbPorts.append(p)
        #self.usbList = selectBox(self.usbmgr, self, usbPorts, 1, 0)
        #self.usbList.grid(sticky = W) # additional 'grid' to get columnspan

        # open/close connection to Grbl button
        self.usbConn = cmdButton(self.usbmgr, self, "Connect", 'connect', 1, 1)
        self.usbConn.configure(width = 8)
        self.usbConn.grid(sticky = W)

        self.usbmgr.grid(row = 0, column = 0, ipadx = 5, ipady = 5, sticky = (N, S, W, E))


        #JOG MANAGER
        self.jogmgr = Frame(self, borderwidth = 2, relief = RIDGE)
        self.jogmgrLabel = Label(self.jogmgr, text = "Jog Axes")
        self.jogmgrLabel.grid(row = 0, column = 0, sticky = SW)

        r = 1
        c = 0

        ## alternative versions of buttons are commented out
        # top row
        self.XmYp = jogButton(self.jogmgr, self, u"\u25F8", 'XmYp', r, c)
        self.Yp = jogButton(self.jogmgr, self, u"\u25B2", 'Yp', r, c + 1)
        self.XpYp = jogButton(self.jogmgr, self, u"\u25F9", 'XpYp', r, c + 2)
        self.Zp = jogButton(self.jogmgr, self, u"\u25B2", 'Zp', r, c + 3)

        # centre row
        self.Xm = jogButton(self.jogmgr, self, u"\u25C0", 'Xm', r + 1, c)
        self.Hm = jogButton(self.jogmgr, self, u"\u263C", 'gotoHm', r + 1, c + 1)
        self.Xp = jogButton(self.jogmgr, self, u"\u25B6", 'Xp', r + 1, c + 2)

        #Jog stepsize combobox
        jogsizes = ['jogsize', '0', '0.01', '0.05', '0.1', '0.5', '1', '5', '10', '50', '100']
        #self.jogsizeList = selectBox(self.jogmgr, self, jogsizes, r + 1, c + 3)
        #self.jogsizeList.configure(width = 5)

        # bottom row
        self.XmYm = jogButton(self.jogmgr, self, u"\u25FA", 'XmYm', r + 2, c)
        self.Ym = jogButton(self.jogmgr, self, u"\u25BC", 'Ym', r + 2, c + 1)
        self.XpYm = jogButton(self.jogmgr, self, u"\u25FF", 'XpYm', r + 2, c + 2)
        self.Zm = jogButton(self.jogmgr, self, u"\u25BC", 'Zm', r + 2, c + 3)

        self.jogmgr.grid(row = 1, column = 0, ipadx = 5, ipady = 5, sticky = (N, S, W, E))


        # POSITION MANAGER
        r = 0
        self.posmgr = Frame(self, borderwidth = 2, relief = RIDGE)
        self.posmgrLabel = Label(self.posmgr, text = "Tool Position")
        self.posmgrLabel.grid(row = 0, column = 0, sticky = SW)

        r += 1
        rowList = ['M Pos', 'W Pos']
        colList = ['X', 'Y', 'Z']
        #self.position = Table(self.posmgr, self, colList, rowList)
        #self.position.grid(row = 1, column = 0, columnspan = 3, sticky = (N, S, W, E))

        r += 1
        c = 0
        self.posMHm = cmdButton(self.posmgr, self, "MachHome", 'gotoMHm', r, c)
        self.posWHm1 = cmdButton(self.posmgr, self, "WorkHome1", 'gotoWHm1', r, c + 1)
        self.posWHm2 = cmdButton(self.posmgr, self, "WorkHome2", 'gotoWHm2', r, c + 2)

        self.posmgr.grid(row = 2, column = 0, ipadx = 5, ipady = 5, sticky = (N, S, W, E))

        # CURRENT JOB MANAGER
        r = 0
        self.jobmgrLabelVar = StringVar()
        self.jobmgrLabelVar.set('Current Job:  --- no file selected ---' )
        self.jobmgr = Frame(self, borderwidth = 2, relief = RIDGE)
        self.jobmgrLabel = Label(self.jobmgr, textvariable = self.jobmgrLabelVar)
        self.jobmgrLabel.grid(row = 0, column = 0, columnspan = 3, sticky = SW)

        self.runS = cmdButton(self.jobmgr, self, "Run (S)", 'sRun', r + 1, c)
        self.runA = cmdButton(self.jobmgr, self, "Run (A)", 'aRun', r + 1, c + 1)
        self.hold = cmdButton(self.jobmgr, self, "Hold", 'hold', r + 1, c + 2)
        self.stop = cmdButton(self.jobmgr, self, "Stop", 'stop', r + 1, c + 3)

        self.jobmgr.grid(row = 3, column = 0, ipadx = 5, ipady = 5, sticky = (N, S, W, E))


        ## RIGHTSIDE CONTROLS
        
        # COMMAND MANAGER
        r = 0
        c = 0
        self.cmdmgr = Frame(self, borderwidth = 2, relief = RIDGE)
        self.cmdmgrLabel = Label(self.cmdmgr, text = "Grbl Commands")
        self.cmdmgrLabel.grid(row = r, column = c, sticky = SW)

        r += 1
        self.homing = cmdButton(self.cmdmgr, self, "Homing $H", 'homing', r, c)
        self.unlock = cmdButton(self.cmdmgr, self, "Unlock $X", 'unlock', r, c + 1)

        self.sReset = cmdButton(self.cmdmgr, self, "Reset (s)", 'sReset', r, c + 2)
        self.hReset = cmdButton(self.cmdmgr, self, "Reset (h)", 'hReset', r, c + 3)


        # Command Entry
        r = 2
        self.cmdEntry = Entry(self.cmdmgr, font = (12), width = 24)
        self.cmdEntry.grid(row = r, column = 0, padx= 10, pady = 10, columnspan = 3, sticky = W)
        self.cmdSend = cmdButton(self.cmdmgr, self, "Send", 'send', 2, 3)

        # Status Window
        self.grblStatusL = Label(self.cmdmgr, text = "Grbl Monitor")
        self.grblStatusL.grid(row = r + 1, column = 0, sticky = W)
        self.grblStatus = Text(self.cmdmgr, width = 40, height = 16, font = (12))
        self.grblStatus.grid(row = r + 2, column = 0, columnspan = 4)

        r = 5
        c = 0
        self.settings = cmdButton(self.cmdmgr, self, "Settings $$", 'settings', r, c)
        self.parameters = cmdButton(self.cmdmgr, self, "Parameters $#", 'parameters', r, c + 1)
        self.parser = cmdButton(self.cmdmgr, self, "Parser $G", 'parser', r, c + 2)
        
        self.gMode = cmdButton(self.cmdmgr, self, "gMode $C", 'gMode', r + 1, c)
        self.startblk = cmdButton(self.cmdmgr, self, "Start blocks $N", 'startblk', r + 1, c + 1)
        self.status = cmdButton(self.cmdmgr, self, "Status ?", 'status', r + 1, c + 2)

        self.cmdmgr.grid(row = 0, column = 1, rowspan = 4, ipadx = 5, ipady = 5, sticky = (N, S, W, E))

        self.grid()

#------------------------------------------------------------------------------------
#       Widgets
#------------------------------------------------------------------------------------

# combobox for: USB port, Jog stepsize
##class selectBox(ttk.Combobox):
##    def __init__(self, master, mainClass, opt_list, r, c):
##        ttk.Combobox.__init__(self, master = master)
##
##        self.optSelected = StringVar()
##        self.configure(values=opt_list[1:], textvariable=self.optSelected, font = (12))
##        self.configure(state = "readonly") # to prevent user typed input
##        self.bind("<<ComboboxSelected>>", lambda *args: mainClass.optionHandler(opt_list[0]))
##        self.grid(row = r, column = c, padx = 5, pady = 5)

# square buttons: dir arrow icons
class jogButton(Button):
    def __init__(self, master, mainClass, btext, motion, r, c):
    #def __init__(self, master, icon, motion, r, c):
        Button.__init__(self, master = master)

        self.configure(text = btext, command = lambda: mainClass.ButtonHandler(motion))
        
        #self.configure(font = tkinter.font.Font(size = 28))
        jogButtFont = ('times', 28, 'normal')
        self.configure(font = jogButtFont)
        
        self.configure(state = "disabled")
        self.grid(row = r, column = c)
        if r == 1: self.grid(pady = (10, 0))
        if c == 0 or c == 3: self.grid(padx = (10, 0))

# rectangular buttons: icons & text
class cmdButton(Button):
    def __init__(self, master, mainClass, btext, action, r, c):
        Button.__init__(self, master = master)

        self.configure(text = btext, command = lambda: mainClass.ButtonHandler(action))
        self.configure(state = "disabled")
        self.grid(row = r, column = c, padx = 5, pady = 2)

#-------------------------------------------------
# MAIN
#-------------------------------------------------

if __name__ == "__main__":
    root = Tk()

    Window = PyGrbl_App(root)
    SubApp1 = Control_Panel(Window.mainFrame)

    root.mainloop()

