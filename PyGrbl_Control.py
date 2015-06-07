#!/usr/bin/python2.7

"""
Grbl_Control

"""

from Tkinter import *
import ttk
import serial, re, glob # cwiid

from PyGrbl_GUI import *
from PyGrbl_ScrollTable import *

class PyGrbl_ControlPanel(Frame):
    def __init__(self, master, app):
        Frame.__init__(self, master = master)

        ##  WHO AM I ?
        #print("Who am I:  " + self.winfo_class())  # = 'Frame' !!
        #print("Who is my parent: " + app.__class__.__name__) # = PyGrbl_GUI
        #print("Who am I:  " + self.__class__.__name__) # = 'PyGrbl_ControlPanel'

        self.app = app
        self.app.servicemenu.entryconfig("Control Panel", state = "normal")
        self.app.apps.append(self.__class__.__name__)
        self.filename = "Selected Job: --- using internal data ---"

        self.JogButtonFont = tkFont.Font(size = int(self.app.fontscale * 2.5))

        app.fileOpenFlag.trace_variable('w', self.fileOpenTraceAction)

        self.jobStreamFlag = BooleanVar() # gCode file streaming complete T/F
        self.jobStreamFlag.set(False)
        self.jobStreamFlag.trace_variable('w', self.jobStreamTraceAction)

        self.jobDoneFlag = BooleanVar() # gCode file milling complete T/F
        self.jobDoneFlag.set(False)
        self.jobDoneFlag.trace_variable('w', self.jobDoneTraceAction)

        self.grblStatus = StringVar()
        self.grblStatus.set('')
        self.grblStatus.trace_variable('w', self.grblStatusTraceAction)
        
        self.create_ControlWidgets()
        
        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)
        self.grid(column = 0, row = 0, sticky = (N, S, W, E))


    def create_ControlWidgets(self):
        ## LEFTSIDE CONTROLS
        # SYSTEM MANAGER
        self.sysmgr = Frame(self, borderwidth = 2, relief = RIDGE, padx = 5, pady = 5)
        Label(self.sysmgr, text = "System Controls").grid(row = 0, column = 0,
                                                          columnspan = 2, sticky = (N, W))

        r = 1
        c = 0
        # open/close connection to Grbl button
        self.grblConn = cmdButton(self.sysmgr, self, "Connect\nGrbl", 'connect', r, c)
        self.grblConn.configure(state = "normal")
        self.grblConn.grid(sticky = (N, S), rowspan = 2)
        self.grblConnFlag = BooleanVar() # Grbl connected T/F
        self.grblConnFlag.set(False)
        self.grblConnFlag.trace_variable('w', self.grblConnTraceAction)

        cmdButton(self.sysmgr, self, "Homing $H", '$H', r, c + 1)
        cmdButton(self.sysmgr, self, "Unlock $X", '$X', r, c + 2)
        cmdButton(self.sysmgr, self, "Reset (s)", 'sReset', r + 1, c + 1)
        cmdButton(self.sysmgr, self, "Reset (h)", 'hReset', r + 1, c + 2)

        self.sysmgr.grid(row = 0, column = 0, sticky = (N, S, W, E))
        for row in range(r + 1):
            self.sysmgr.rowconfigure(row, weight = 1)
        for col in range(c + 2):
            self.sysmgr.columnconfigure(col, weight = 1)


        # POSITION MANAGER
        r = 0
        c = 0
        self.posmgr = Frame(self, borderwidth = 2, relief = RIDGE, padx = 5, pady = 5)
        Label(self.posmgr, text = "Tool Position").grid(row = r, column = c, sticky = NW)

        r += 1
        colList = ['M Pos', 'W Pos']
        rowList = ['X', 'Y', 'Z']
        self.posTable = Table(self.posmgr, self, colList, rowList)
        self.posTable.grid(row = r, column = c, rowspan = 3, sticky = (W))

        self.Mx = StringVar()
        self.Mx.set('')
        self.My = StringVar()
        self.My.set('')
        self.Mz = StringVar()
        self.Mz.set('')
        self.Wx = StringVar()
        self.Wx.set('')
        self.Wy = StringVar()
        self.Wy.set('')
        self.Wz = StringVar()
        self.Wz.set('')

        self.posVars = [[self.Mx, self.My, self.Mz], [self.Wx, self.Wy, self.Wz]]
        self.posTable.fill_TableV(self.posVars)
        
        cmdButton(self.posmgr, self, "MHm", 'gotoMHm', r , c + 1)
        cmdButton(self.posmgr, self, "WHm1", 'gotoWHm1', r + 1, c + 1)
        cmdButton(self.posmgr, self, "WHm2", 'gotoWHm2', r + 2, c + 1)

        self.posmgr.grid(row = 1, column = 0, sticky = (N, S, W, E))
        for row in range(r + 2):
            self.posmgr.rowconfigure(row, weight = 1)
        self.posmgr.columnconfigure(0, weight = 1)

        # CURRENT JOB MANAGER
        r = 0
        self.jobmgrLabelVar = StringVar()
        self.jobmgrLabelVar.set('Current Job:  --- no file selected ---' )

        self.jobmgr = Frame(self, borderwidth = 2, relief = RIDGE, padx = 5, pady = 5)
        Label(self.jobmgr, textvariable = self.jobmgrLabelVar).grid(row = 0, column = 0,
                                                                    columnspan = 3, pady = (0, 10), sticky = SW)

        self.sRun = cmdButton(self.jobmgr, self, "Run (S)", 'sRun', r + 1, c)
        self.aRun = cmdButton(self.jobmgr, self, "Run (A)", 'aRun', r + 2, c)
        self.runJobFlag = BooleanVar() # run Job button pressed
        self.runJobFlag.set(False)
        self.runJobFlag.trace_variable('w', self.runJobTraceAction)

        self.hold = cmdButton(self.jobmgr, self, "Hold", 'hold', r + 1, c + 1)
        self.hold.grid(rowspan = 2, sticky = (N, S))
        self.holdJobFlag = BooleanVar() # hold button pressed T/F
        self.holdJobFlag.set(False)
        self.holdJobFlag.trace_variable('w', self.holdJobTraceAction) # trace needed ?

        self.stop = cmdButton(self.jobmgr, self, "Stop", 'stop', r + 1, c + 2)
        self.stop.grid(rowspan = 2, sticky = (N, S))
        self.stopJobFlag = BooleanVar() # stop button pressed T/F
        self.stopJobFlag.set(False)
        self.stopJobFlag.trace_variable('w', self.stopJobTraceAction) # trace needed ?

        self.jobmgr.grid(row = 2, column = 0, sticky = (N, S, W, E))
        for row in range(r + 1):
            self.sysmgr.rowconfigure(row, weight = 1)
        for col in range(c + 2):
            self.sysmgr.columnconfigure(col, weight = 1)


        ## RIGHTSIDE CONTROLS
        ## NOTEBOOK
        self.nBook = ttk.Notebook(self)
        self.nBook.grid(row = 0, column = 1, rowspan = 4,
                        padx = 5, pady = 5, sticky = (N, S, W, E))

        for col in range(2):
            self.columnconfigure(col, weight = 1)
        for row in range(3):
            self.rowconfigure(row, weight = 1)
        
        # Monitor Tab
        self.monitor = Frame(self.nBook, padx = 5, pady = 5)
        self.nBook.add(self.monitor, text = "Monitor")

        r = 0
        c = 0
        Label(self.monitor, text = "Grbl Monitor").grid(row = r, column = c, sticky = W)

        r += 1
        self.cmdEntry = Entry(self.monitor, width = 20, state = "disabled")
        self.cmdEntry.grid(row = r, column = c, sticky = W)
        self.cmdSendM = cmdButton(self.monitor, self, "Send", 'sendm', r, c + 1)
        self.cmdSendM.grid(sticky = W)

        r += 1
        self.grblMonitor = ScrolledText(self.monitor, width = 24, height = 12, state = "disabled")
        self.grblMonitor.grid(row = r, column = 0, columnspan = 2, sticky = (N, S, W, E))
        
        self.monitor.rowconfigure(r, weight = 1)
        self.monitor.columnconfigure(0, weight = 1)

        # Query Tab
        self.qrymgr = Frame(self.nBook, padx = 5, pady = 5)
        self.nBook.add(self.qrymgr, text = "Query")

        r = 0
        c = 0
        buttons = [["Settings $$", '$$'] ,["Param $#", '$#'], ["Parser $G", '$G'],
                   ["Start blks $N", '$N'], ["Status ?", '?'], ["Help $", '$']]
        for b in buttons:
            qryButton(self.qrymgr, self, b[0], b[1], r, c)
            c +=1
            if c > 2:
                c = 0
                r += 1

        self.qryMonitor = ScrolledText(self.qrymgr, width = 36, height = 14, state = "disabled")
        self.qryMonitor.grid(row = r, column = 0, columnspan = 3, sticky = (N, S, W, E))
        
        self.qrymgr.rowconfigure(r, weight = 1)
        self.qrymgr.columnconfigure(2, weight = 1)

        # Quick Command Tab
        self.cmdmgr = Frame(self.nBook, padx = 5, pady = 5)
        self.nBook.add(self.cmdmgr, text = "Quick Cmd")

        r = 0
        c = 0
        self.keyF = keyButton(self.cmdmgr, self, ["F", 'f'], r, c)

        buttons = [["-100", "fm100"], ["-10", "fm10"], ["+10", "fp10"], ["+100", "fp100"]]
        self.fVar = IntVar()
        self.fVar.set(100)
        incDecBar(self.cmdmgr, self, buttons, self.fVar).grid(row = r, column = c + 1, columnspan = 3)

        r += 1
        ttk.Separator(self.cmdmgr, orient=HORIZONTAL).grid(row = r, column = c,
                                                           columnspan = 4, pady = 10, sticky = (W, E))

        r += 1
        buttons = [["X", "x"] ,["Y", "y"], ["Z", "z"]]
        keyBar(self.cmdmgr, self, buttons).grid(row = r, column = c, columnspan = 2, sticky = W)

        buttons = [["I", "i"],["J", "j"]]
        keyBar(self.cmdmgr, self, buttons).grid(row = r, column = c + 2, columnspan = 2, sticky = W)

        c = 0
        r += 1
        buttons = [["-100", "mm100"], ["-10", "mm10"], ["-1", "mm1"], ["+1", "mp1"], ["+10", "mp10"], ["+100", "mp100"]]
        self.mVar = IntVar()
        self.mVar.set(100)
        incDecBar(self.cmdmgr, self, buttons, self.mVar).grid(row = r, column = c,
                                                         columnspan = 4, pady = (5, 0))

        ttk.Separator(self.cmdmgr, orient=HORIZONTAL).grid(row = r + 1, column = c,
                                                           columnspan = 4, pady = 10, sticky = (W, E))

        r += 2
        buttons = [["G0", "g0"] ,["G1", "g1"], ["G2", "g2"], ["G3", "g3"]]
        keyBar(self.cmdmgr, self, buttons).grid(row = r, column = c, columnspan = 2)

        buttons = [["G90", "g90"],["G91", "g91"]]
        keyBar(self.cmdmgr, self, buttons).grid(row = r, column = c + 2, columnspan = 2)

        c = 0
        ttk.Separator(self.cmdmgr, orient=HORIZONTAL).grid(row = r + 1, column = c,
                                                           columnspan = 4, pady = 10, sticky = (W, E))

        r += 2
        self.gCodeCmd = StringVar()
        self.gCodeCmd.set('gCodeCmd')
        Label(self.cmdmgr, textvariable = self.gCodeCmd, width = 16,
              relief = SUNKEN).grid(row = r, column = c, columnspan = 2, padx= 5, pady = 2, sticky = W)

        self.cmdSendB = cmdButton(self.cmdmgr, self, "Send", 'sendb', r, c + 2)
        self.cmdClear = cmdButton(self.cmdmgr, self, "Clear", 'clear', r, c + 3)

        r += 1
        self.cmdMonitor = ScrolledText(self.cmdmgr, width = 16, height = 4, state = "disabled")
        self.cmdMonitor.grid(row = r, column = c, columnspan = 4, sticky = (N, S, W, E))
        
        self.cmdmgr.rowconfigure(r, weight = 1)
        self.cmdmgr.columnconfigure(3, weight = 1)


        # Jog Tab
        self.jogmgr = Frame(self.nBook, padx = 5, pady = 5)
        self.nBook.add(self.jogmgr, text = "Jog Axes")

        r = 0
        c = 0
        # jog size
        Label(self.jogmgr, text = "Jog size").grid(row = r, column = c, sticky = W)

        self.jgVars = ['0', '0.01', '0.05', '0.1', '0.5', '1', '5', '10', '50', '100']
        self.jgIndex = 1
        self.jgVar = StringVar()
        self.jgVar.set(self.jgVars[self.jgIndex])

        options = [["-", "jgm"], ["+", "jgp"]]
        incDecBar(self.jogmgr, self, options, self.jgVar).grid(row = r,
                                                               column = c + 1, pady = (5, 0), sticky = W)

        r += 1
        buttons = [[[u"\u25F8", 'XmYp'], [u"\u25B2", 'Yp'], [u"\u25F9", 'XpYp'], [u"\u25B2", 'Zp']],
                   [[u"\u25C0", 'Xm'], [u"\u263C", 'gotoHm'], [u"\u25B6", 'Xp'], ["", ""]],
                   [[u"\u25FA", 'XmYm'], [u"\u25BC", 'Ym'], [u"\u25FF", 'XpYm'], [u"\u25BC", 'Zm']]]
        jogPanel(self.jogmgr, self, buttons).grid(row = r, column = c,
                                                  columnspan = 2, sticky = W)

        r += 1
        # jog monitor
        self.jogMonitor = ScrolledText(self.jogmgr, width = 20, height = 4, state = "disabled")
        self.jogMonitor.grid(row = r, column = c, columnspan = 2, padx = 5, pady = 5, sticky = (N, S, W, E))

        self.jogmgr.rowconfigure(r, weight = 1)
        self.jogmgr.columnconfigure(1, weight = 1)


        # Configure Tab
        self.configmgr = Frame(self.nBook, padx = 5, pady = 5)
        self.nBook.add(self.configmgr, text = "Configure")

        r = 0
        c = 0
        # USB Port
        Label(self.configmgr, text = "Select USB Port: ").grid(row = r, column = c, padx = 2, pady = 2)
        self.usbPorts = ['/dev/ttyUSB0']
        self.usbList = selectBox(self.configmgr, self, self.usbPorts, r, c + 1)
        self.usbList.grid(columnspan = 2, sticky = W) # additional 'grid' to get columnspan

        self.usbRefresh = Button(self.configmgr, text = "Refresh", command = lambda: self.ButtonHandler('refreshUSBList'))
        self.usbRefresh.grid(row = r + 1, column = c)

        ttk.Separator(self.configmgr, orient=HORIZONTAL).grid(row = r + 2, column = c,
                                                           columnspan = 3, pady = 10, sticky = (W, E))

        # wiimote pendant
        r += 3
        Label(self.configmgr, text = "WiiMote (Bluetooth): ").grid(row = r,
                                                                    column = c, columnspan = 2, padx = 2, pady = 2)
        self.wiiConn = cmdButton(self.configmgr, self, "Connect", 'wiiConnect',  r,  c + 2)
        self.wiiConn.configure(state = "disabled")
        self.wiiConn.grid()

        ttk.Separator(self.configmgr, orient=HORIZONTAL).grid(row = r + 1, column = c,
                                                              columnspan = 3, pady = 10, sticky = (W, E))

        # Grbl gCode Mode (Live / Check)
        r += 2
        Label(self.configmgr, text = "Grbl gCode Mode ($C): ").grid(row = r,
                                                                column = c, columnspan = 2, padx = 2, pady = 2)
        self.gCodeMode = cmdButton(self.configmgr, self, "Live", '$C',  r,  c + 2)
        self.gCodeMode.configure(state = "disabled")

        ttk.Separator(self.configmgr, orient=HORIZONTAL).grid(row = r + 1, column = c,
                                                           columnspan = 3, pady = 10, sticky = (W, E))

##        # Bluetooth
##        r += 2
##        Label(self.configmgr, text = "Bluetooth Status: ").grid(row = r, column = c, padx = 2, pady = 2)
##
##        self.btTest = Button(self.configmgr, text = "Test", command = lambda: self.ButtonHandler('btTest'))
##        self.btTest.grid(row = r, column = c + 1)
##
##        self.btReset = Button(self.configmgr, text = "Reset", command = lambda: self.ButtonHandler('btReset'))
##        self.btReset.grid(row = r, column = c + 3)
        
#-------------------------------------------------------------------------------
#       PyGrbl_ControlPanel METHODS
#-------------------------------------------------------------------------------
#       Core
#           todo:   placeholder during development
#           setWstate:  set the state of a single widget
#           setWCstate:  set the state of a class of widgets in the specified frame
#
#       Event handler methods
#           buttonhandler:  all ControlPanel button commands start here
#
#           variable trace handlers
#               fileOpenTraceAction:  ControlPanel action following fileOpen
#               grblConnTraceAction:  action following connection to Grbl
#               runJobTraceAction:  action following variable update when Run button pressed
#               jobStreamTraceAction:
#               jobDoneTraceAction:
#               holdJobTraceAction:
#               stopJobTraceAction:
#               grblStatusTraceAction:
#
#           button actions
#               refreshUSBList:
#               toggleUSBPort:
#               toggleWiimote:
#               sendPreset:
#               sendCommand:
#               buildCmd:
#               jogMotor:
#               runJob:
#               checkStatus:
#               grblReset:
#
#       Streaming methods
#           simpleStream:
#           simpleAfterLoop:
#           aggressiveStream:
#           aggAfterLoopSend:
#           aggAfterLoopRec:
#
#       Read / Write methods
#           writeBlock
#           readResponses
#           readResponse
#           postInfo:  display grbl feedback
#           sendInfoRequest:  send / receiving specific info as part of running jobs
#

    def todo(self): # placeholder during development
        pass

    def setWstate(self, widget, newState): # set state of individual widget
        widget.configure(state = newState)

    def setWCstate(self, frame, widgetTypes, newState): # set state of class of widgets in parent frame
        for child in frame.winfo_children():
            if child.winfo_children():
                self.setWCstate(child, widgetTypes, newState)
            else:
                if child.__class__.__name__ in widgetTypes:
                    child.configure(state = newState)

    def printChildList(self, widget):
        for child in widget.winfo_children():
            if child.winfo_children():
                self.printChildList(child)
            else:
                print(child.__class__.__name__)


#-------------------------------------------------------------------------------
#       Event Handler methods
#-------------------------------------------------------------------------------
    def ButtonHandler(self, request): # button handler - all button commands start here !!!
        if self.app.debugMode > 1: print("Button Handler: " + request)

        if request == 'connect': self.toggleUSBPort() #self.sysConn
        elif request =='wiiConnect': self.toggleWiimote() # self.wiiConn
        elif request == 'sReset': self.grblReset('soft') # self.sReset
        elif request == 'hReset': self.grblReset('hard') # self.hReset
        elif request == 'sendm': self.sendCommand("M") # manual command entry
        elif request == 'response': self.readResponse() # manual check response buffer

        #Presets:  buttons on 'system control', 'query tab', 'configure tab'
        elif request in ['$$', '$#', '$G', '$N', '?', '$', '$H', '$X', '$C']:
            self.sendPreset(request)

        #self.posMHm, self.posWHm1, self.posWHm2, self.sRun, self.aRun, self.hold, self.stop
        elif request == 'gotoMHm': self.goHome("G28")
        elif request == 'gotoWHm1': self.goHome("G30")
        elif request == 'gotoWHm2': self.goHome("G30")
        elif request == 'sRun': self.runJob('simple')
        elif request == 'aRun': self.runJob('aggressive')
        elif request == 'hold': self.holdJobFlag.set(not self.holdJobFlag.get())
        elif request == 'stop': self.stopJobFlag.set(not self.stopJobFlag.get())

        #command builder
        elif request == 'f': self.buildCmd('F')
        elif request == 'fm100' : self.fVar.set(self.fVar.get() - 100)
        elif request == 'fm10' : self.fVar.set(self.fVar.get() - 10)
        elif request == 'fp10' : self.fVar.set(self.fVar.get() + 10)
        elif request == 'fp100' : self.fVar.set(self.fVar.get() + 100)

        elif request in ['x', 'y', 'z', 'i', 'j']:
            self.buildCmd(request.upper())

        elif request == 'mm100' : self.mVar.set(self.mVar.get() - 100)
        elif request == 'mm10' : self.mVar.set(self.mVar.get() - 10)
        elif request == 'mm1' : self.mVar.set(self.mVar.get() - 1)
        elif request == 'mp1' : self.mVar.set(self.mVar.get() + 1)
        elif request == 'mp10' : self.mVar.set(self.mVar.get() + 10)
        elif request == 'mp100' : self.mVar.set(self.mVar.get() + 100)

        elif request in ['g0', 'g1', 'g2', 'g3', 'g90', 'g91']:
            self.buildCmd(request.upper())

        elif request == 'sendb': self.sendCommand("B")
        elif request == 'clear': self.gCodeCmd.set('')

        elif request in ['jgp', 'jgm']:
            if request =='jgp' and self.jgIndex < 9:
                self.jgIndex += 1
            elif request == 'jgm' and self.jgIndex > 0:
                self.jgIndex -= 1
            self.jgVar.set(self.jgVars[self.jgIndex])

        elif request in ['XmYp', 'Yp', 'XpYp', 'Xm', 'Xp', 'XmYm', 'Ym', 'XpYm', 'Zp', 'Zm']:
            jog = self.jgVar.get()
            temp = ''
            if request.find('Xm') >= 0: temp += 'X-' + jog
            if request.find('Xp') >= 0: temp += 'X' + jog
            if request.find('Ym') >= 0: temp += 'Y-' + jog
            if request.find('Yp') >= 0: temp += 'Y' + jog
            if request.find('Zm') >= 0: temp += 'Z-' + jog
            if request.find('Zp') >= 0: temp += 'Z' + jog
            self.jogMotor(temp)

        elif request == 'gotoHm': print('goto temp home (configure?)')
        elif request == 'refreshUSBList': self.refreshUSBList()


#-------------------------------------------------------------------------------
#       Variable Trace Actions
#-------------------------------------------------------------------------------
    def fileOpenTraceAction(self, name, index, mode):
        if self.app.fileOpenFlag.get():
            if self.grblConnFlag.get():
                self.setWstate(self.sRun, "normal")
                self.setWstate(self.aRun, "normal")
                self.setWstate(self.hold, "disabled")
                self.setWstate(self.stop, "disabled")
        else:
            widgetTypes = ["cmdButton"]
            self.setWCstate(self.jobmgr, widgetTypes, "disabled")

    def grblConnTraceAction(self, name, index, mode):
        if self.grblConnFlag.get() == True:
            widgetTypes = ["cmdButton", "qryButton", "keyButton", "jogButton", "incDecButt"]
            self.setWCstate(self, widgetTypes, "normal")
            self.cmdEntry.configure(state = "normal")

            if self.app.fileOpenFlag.get() :
                self.setWstate(self.hold, "disabled")
                self.setWstate(self.stop, "disabled")
            else:
                widgetTypes = ["cmdButton"]
                self.setWCstate(self.jobmgr, widgetTypes, "disabled")

        else:
            widgetTypes = ["cmdButton", "qryButton", "keyButton", "jogButton", "incDecButt"]
            self.setWCstate(self, widgetTypes, "disabled")
            self.cmdEntry.configure(state = "disabled")
            for w in [self.grblMonitor, self.qryMonitor, self.cmdMonitor, self.jogMonitor]:
                w.configure(state = "normal")
                w.delete(1.0, END)
                w.configure(state = "disabled")
            self.setWstate(self.grblConn, "normal")

    def runJobTraceAction(self, name, index, mode):
        if self.runJobFlag.get() == True:
            widgetTypes = ["cmdButton", "qryButton", "keyButton", "jogButton", "incDecButt"]
            self.setWCstate(self, widgetTypes, "disabled")
            self.setWstate(self.grblConn, "normal")
            self.setWstate(self.hold, "normal")
            self.setWstate(self.stop, "normal")
        else:
            widgetTypes = ["cmdButton", "qryButton", "keyButton", "jogButton", "incDecButt"]
            self.setWCstate(self, widgetTypes, "normal")
            self.setWstate(self.hold, "disabled")
            self.setWstate(self.stop, "disabled")

    def jobStreamTraceAction(self, name, index, mode):
        if self.jobStreamFlag.get() == True:
            self.postInfo('grblMonitor', '--  gCode Streaming Complete  --')
            self.jobStreamFlag.set(False)

    def jobDoneTraceAction(self, name, index, mode):
        if self.jobDoneFlag.get() == True:
            self.postInfo('grblMonitor', '--  gCode Job Complete  --')
            self.jobDoneFlag.set(False)
            self.runJobFlag.set(False) # resets button states?

    def holdJobTraceAction(self, name, index, mode):
        if self.holdJobFlag.get() == True:
            self.hold['text'] = 'Resume'
            self.postInfo('grblMonitor', 'Sending:  Hold')
            self.update_idletasks()
            self.sendPreset('!')
            self.readResponse()
        else:
            self.hold['text'] = 'Hold'
            self.postInfo('grblMonitor', 'Sending:  Resume')
            self.update_idletasks()
            self.sendPreset('~')
            self.readResponse()

    def stopJobTraceAction(self, name, index, mode):
        self.postInfo('grblMonitor', 'Sending:  STOP !')
        self.update_idletasks()
        self.sendPreset('!')
        self.readResponse()
        self.runJobFlag.set(False) # resets button states?

    def grblStatusTraceAction(self, name, index, mode):
        status = self.grblStatus.get()
        status = re.sub('<|>', '', status)
        statusList = []
        statusList = re.split(',|:', status)
        if statusList[0] == 'Run' or statusList[0] == 'Idle':
            self.Mx.set(statusList[2])
            self.My.set(statusList[3])
            self.Mz.set(statusList[4])
            self.Wx.set(statusList[6])
            self.Wy.set(statusList[7])
            self.Wz.set(statusList[8])

        self.app.statusbarList[1] = "Grbl Status: " + statusList[0]
        statusInfo = ""
        for info in self.app.statusbarList:
            if info != "": statusInfo = statusInfo + info + " | "
        self.app.statusbarText.set(statusInfo)

#-------------------------------------------------------------------------------
#       Button Actions
#-------------------------------------------------------------------------------

    def refreshUSBList(self):
        self.usbPorts = []
        ports = (glob.glob('/dev/tty[A-Za-z]*'))
        for p in ports: self.usbPorts.append(p)
        self.update_idletasks()
        
        self.usbList.configure(state = "normal")
        self.usbList.configure(values=self.usbPorts, font = (12))
        self.usbList.configure(state = "readonly")
        self.usbList.current(0)

    def toggleUSBPort(self):
        #print("ToggleUSBPort")
        # print(self.togglePort.cget("bg"))
        # default col (grey) #d9d9d9
        # red #ff8080
        # green #d8f6ce

        try:
            if self.grblConn["text"] == "Connect\nGrbl":
                try:
                    self.usbPort = self.usbList.get()
                    #self.serPort = serial.Serial("/dev/ttyACM0", baudrate = 115200, timeout = 1)
                    self.serPort = serial.Serial(self.usbPort, baudrate = 115200, timeout = 2)
                    time.sleep(2)
                    self.writeBlock('\r')
                    self.readResponses()
                    self.serPort.flushInput()
                    self.grblConnFlag.set(True)
                    self.grblConn.configure(text = "Disconnect\nGrbl", bg = "#bdcbf6")
                    self.app.statusbarText.set("System Status: Grbl Connected")
                    self.checkGrblStatus()
                    if self.app.debugMode > 1: print("Serial Connect: Ok")
                except:
                    print("Serial Connect: Error")
                    self.app.statusbarText.set("System Status: Unable to Connect Grbl")

            elif self.grblConn["text"] == "Disconnect\nGrbl":
                try:
                    self.serPort.close()
                    self.grblConnFlag.set(False)
                    self.grblConn.configure(text = "Connect\nGrbl", bg = "#d9d9d9", state = "normal")
                    self.app.statusbarText.set("System Status: Grbl Disconnected")
                    if self.app.debugMode > 1: print("Serial Disconnect:Ok")
                except:
                    print("Serial Disconnect: Error")
                    self.app.statusbarText.set("System Status: Grbl Not Responding")

        except:
            print("ToggleUSBPort Error")
            self.app.statusbarText.set("System Status: USB port / Grbl not responding")

    def toggleWiimote(self):
        try:
            if self.app.wiiState == 'Disconnected':
                try:
                    self.app.wiiMote.wiiConnect()
                    if self.app.wiiState == 'Connected':
                        self.wiiConn.configure(text = "Disconnect", bg = "#bdcbf6")
                    if self.app.debugMode > 1: print("Wii Connect: Ok")
                except:
                    if self.app.debugMode > 0: print("Wii Connect: Error")

            elif self.app.wiiState =='Connected':
                try:
                    self.app.wiiMote.wiiStop()
                    if self.app.wiiState == 'Disconnected':
                        self.wiiConn.configure(text = "Connect", bg = "#d9d9d9", state = "normal")
                    if self.app.debugMode > 1: print("Wii Disconnect:Ok")
                except:
                    if self.app.debugMode > 0: print("Wii Disconnect: Error")

        except:
            if self.app.debugMode > 0: print("ToggleWiimote Error")

    def sendPreset(self, preset):
        if preset in ['$$', '$#', '$G', '$N', '?', '$']: #\n to be added where needed
            monitor = 'qryMonitor'
        else:
            monitor = 'grblMonitor'
        self.writeBlock(preset, monitor)
        time.sleep(2)
        self.readResponses(monitor)

    def sendCommand(self, sendType):
        try:
            if sendType == "M":
                postBoard = "grblMonitor"
                command = self.cmdEntry.get()
                self.cmdSendM.configure(state = "disabled")
            else:
                postBoard = "cmdMonitor"
                command = self.gCodeCmd.get()
                self.gCodeCmd.set("")
                self.cmdSendB.configure(state = "disabled")
                
            self.writeBlock(command, postBoard)
            time.sleep(2)
            self.readResponses(postBoard)

            if sendType == "M": self.cmdSendM.configure(state = "normal")
            else: self.cmdSendB.configure(state = "normal")

        except:
            print("SendCommand Error")

    def buildCmd(self, cmd):
        if self.gCodeCmd.get() == "gCodeCmd":
            self.gCodeCmd.set("")

        currCmd = self.gCodeCmd.get()
        if cmd == 'F':
            addCmd = cmd + str(self.fVar.get())
        elif cmd in ['X', 'Y', 'Z', 'I', 'J']:
            addCmd = cmd + str(self.mVar.get())
        else:
            addCmd = cmd

        self.gCodeCmd.set(currCmd + addCmd)

    def jogMotor(self, action):
        if True:
            self.setWCstate(self.jogmgr, "jogButton", "disabled")
            self.setWCstate(self.posmgr, "cmdButton", "disabled")
            self.writeBlock('G91' + action, 'jogMonitor')
            self.readResponse('jogMonitor')
            self.writeBlock('G90', 'jogMonitor')
            self.readResponse('jogMonitor')
            self.checkJog()

            if self.app.debugMode > 1: print("jogMotor: Ok")
        #except:
            #print("jogMotor: Error")

    def checkJog(self):
        if True:
            self.writeBlock('?', 'silent')
            time.sleep(2)
            self.readResponse('silent') # will refresh grblStatus if a status response is received
            self.readResponse('silent') # will refresh grblStatus if a status response is received

            status = self.grblStatus.get()
            if status.find('Run') >= 0:
                self.after(50, self.checkJog)
                self.update_idletasks()
            else: # when 'Run' ends TO DO: better checking in case of error
                self.setWCstate(self.jogmgr, "jogButton", "normal") # TO DO: don't execute until 'idle' !!!
                self.setWCstate(self.posmgr, "cmdButton", "normal")

            if self.app.debugMode > 1: print("checkJog: Ok")
        #except:
            #print("checkJog: Error")

    def goHome(self, home):
        if True:
            self.writeBlock(home)
            self.readResponse()
            self.checkHome()

            if self.app.debugMode > 1: print("goHome: Ok")
        #except:
            #print("goHome: Error")

    def checkHome(self):
        if True:
            self.writeBlock('?', 'silent')
            time.sleep(2)
            self.readResponse('silent') # will refresh grblStatus if a status response is received
            self.readResponse('silent') # second read to capture accompanying 'ok'

            status = self.grblStatus.get()
            if status.find('Idle') < 0:
                self.after(50, self.checkHome)
                self.update_idletasks()

            if self.app.debugMode > 1: print("checkHome: Ok")
        #except:
            #print("checkHome: Error")

    def runJob(self, runType):
        ok2go = self.sendInfoRequest('Feedrate')

        if ok2go:
            self.runJobFlag.set(True)
            self.update_idletasks()

            # clear input buffer so that response stream is not corrupted
            # by late responses to earlier sends
            self.serPort.flushInput()
            gCodeList = []

            if 'PyGrbl_gCodeChecker' in self.app.apps:
                for line in self.app.gCodeData[3]:
                    if line != '': gCodeList.append(line.strip())
            else:
                for line in self.app.inFile:
                    if line != '': gCodeList.append(line.strip())
                self.app.inFile.seek(0) # reset inFile cursor to top of file

            if runType == "simple": self.simpleStream(gCodeList)
            else: self.aggressiveStream(gCodeList)
            
    def checkGrblStatus(self):
        # check status while/after streaming code
        # return button states once 'idle' received
        self.writeBlock('?', 'silent')
        time.sleep(2)
        self.readResponse('silent') # will refresh grblStatus if a status response is received
        self.readResponse('silent') # will refresh grblStatus if a status response is received

        status = self.grblStatus.get()
        if status.find('Run') >= 0:
            self.after(500, self.checkGrblStatus)
        else:
            if self.runJobFlag.get() == True:
                self.jobDoneFlag.set(True)

    def grblReset(self, resetType): # TO DO: different for soft/hard
        self.sendPreset('!') # feedhold will control deceleration
        time.sleep(2)
        self.sendPreset('\x18')
        self.serPort.flushInput() # clear input buffer too!
        

#-------------------------------------------------------------------------------
#       Stream gCode using Simple call response method
#-------------------------------------------------------------------------------

    def simpleStream(self, gCodeList):
        print("simpleStream")
        # Must be used if sending streaming settings (read below)

        # Send gCode by simple call-response streaming method. Settings must be streamed
        # in this manner since the EEPROM accessing cycles shut-off the serial interrupt.

        self.l_count = 0
        self.l_block = ''
        self.gCodeList = gCodeList

        self.simpleAfterLoop()

    def simpleAfterLoop(self):  ## allows interrupts to stream loop
        doNextFlag = not (self.holdJobFlag.get() or self.stopJobFlag.get())

        if doNextFlag:
            line = self.gCodeList[self.l_count]
            self.l_count += 1
            self.l_block = line.strip()
            self.writeBlock(self.l_block)
            #info = 'SND: ' + str(self.l_count) + ':' + self.l_block
            #self.postInfo('grblMonitor', info)

            self.readResponse()

        if self.l_count < len(self.gCodeList) and not self.stopJobFlag.get():
            self.after(100, self.simpleAfterLoop) # schedule next iteration of the loop
        else:
            self.jobStreamFlag.set(True)
            self.checkGrblStatus()

#-------------------------------------------------------------------------------
#       Stream gCode using 'Aggressive Buffer' method
#-------------------------------------------------------------------------------

    def aggressiveStream(self, gCodeList):

        # Send g-code program via an agressive streaming protocol that forces characters into
        # Grbl's serial read buffer to ensure Grbl has immediate access to the next g-code command
        # rather than wait for the call-response serial protocol to finish. This is done by careful
        # counting of the number of characters sent by the streamer to Grbl and tracking Grbl's
        # responses, such that we never overflow Grbl's serial read buffer.

        self.l_count = 0
        self.g_count = 0
        self.gCodeList = gCodeList
        self.l_block = ''
        self.c_line = []
        self.BUFFER_SIZE = 128

        # Send gCode to Grbl Buffer
        self.aggAfterLoopSend()

        # Wait for remaining responses
        self.aggAfterLoopRec()


    def aggAfterLoopSend(self):
        doNextFlag = not (self.holdJobFlag.get() or self.stopJobFlag.get())

        if doNextFlag:
            line = self.gCodeList[self.l_count]
            self.l_count += 1
            self.l_block = line.strip()
            self.c_line.append(len(self.l_block)+1)

            #while buffer full and waiting for response WAIT !
            while sum(self.c_line) >= self.BUFFER_SIZE - 1 or self.serPort.inWaiting() :
                out_temp = self.readResponse()
                if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
                    self.postInfo('grblMonitor', "Debug:  ")
                    self.postInfo('grblMonitor', out_temp)
                else :
                    grbl_out = out_temp
                    self.g_count += 1
                    del self.c_line[0]

                    #self.postInfo('grblMonitor', "REC: " + str(self.g_count) + " : " + grbl_out)

            # once space available in buffer add next line
            self.writeBlock(self.l_block)
            #self.postInfo('grblMonitor', "SND: " + str(self.l_count) + " : " + self.l_block)
            #self.postInfo('grblMonitor', "BUF: " + str(sum(self.c_line)))

        if self.l_count < len(self.gCodeList) and not self.stopJobFlag.get():
            self.after(100, self.aggAfterLoopSend) # schedule next iteration of the loop


    def aggAfterLoopRec(self): # collect the remaining responses
        doNextFlag = not (self.holdState or self.stopJobFlag.get())

        if doNextFlag:
            if sum(self.c_line) > 0 or self.serPort.inWaiting():
                out_temp = self.readResponse()
                if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
                    response = "Debug:  " + out_temp
                    self.postInfo('grblMonitor', response)
                else :
                    grbl_out = out_temp
                    self.g_count += 1
                    del self.c_line[0]

                    #self.postInfo('grblMonitor', "REC: " + str(self.g_count) + " : " + grbl_out)
                    #self.postInfo('grblMonitor', "BUF: " + str(sum(self.c_line)))

        if self.g_count < len(self.gCodeList) and not self.stopJobFlag.get():
            self.after(100, self.aggAfterLoopRec) # schedule next iteration of the loop
        else:
            self.jobStreamFlag.set(True)

#-------------------------------------------------------------------------------
#       Read / Write methods
#-------------------------------------------------------------------------------

    def writeBlock(self, block, postBoard = 'grblMonitor'):
        try:
            gCode_block = block +'\n' # \n to be removed from here
            self.serPort.write(gCode_block)
            if postBoard != 'silent':
                self.postInfo(postBoard, '->' + block)

        except:
            print("WriteBlock Error")

    def readResponses(self, postBoard = 'grblMonitor'):
        if self.app.debugMode > 1: print("readResponses")
        reachedEnd = False

        while not reachedEnd:
            #response = self.serPort.readline().decode('ascii') # python3
            response = (self.serPort.readline()).strip() # python2.7
            if postBoard != 'silent':
                self.postInfo(postBoard, '<-' + response)            
            if response.find('ok') > 0 or response.find('error') > 0:
                reachedEnd = True
            try:
                if response[0] == '<':
                    self.grblStatus.set(response)
            except:
                pass

        ## TO DO: convert to 'after' so that delayed and multiple responses are picked up
        ## eg $C gives ok to command and then ok following reset

        ##  OR do I actually want read responses to be blocking ??, what if app freezes
    
    def readResponse(self, postBoard = 'grblMonitor'):
        if self.app.debugMode > 1: print("readResponse")
        #response = self.serPort.readline().decode('ascii') # python3
        response = (self.serPort.readline()).strip() # python2.7
        if response:
            if postBoard != 'silent':
                self.postInfo(postBoard, '<-' + response)
            if response[0] == '<':
                self.grblStatus.set(response)
        return response # used by aggressive stream

    def postInfo(self, postBoard, info):
        if self.app.debugMode > 1: print("Post Info")

        if postBoard == 'qryMonitor':
            monitor = self.qryMonitor
        elif postBoard == 'cmdMonitor':
            monitor = self.cmdMonitor
        elif postBoard == 'jogMonitor':
            monitor = self.jogMonitor
        else: monitor = self.grblMonitor
            
        monitor.configure(state = "normal")
        monitor.insert(END, info.strip() + '\n')
        self.update_idletasks()
        monitor.see(END)
        monitor.configure(state = "disabled")

    def sendInfoRequest(self, request):
        if self.app.debugMode > 1: print('sendInfoRequest')
        ok2go = True
        info = 'ok'

        if request == 'Feedrate':
            self.writeBlock('$G')
            time.sleep(2)

            # $G reply
            #response = self.serPort.readline().decode('ascii') # python3
            response = self.serPort.readline() # python2.7
            info = response.strip()
            self.postInfo('grblMonitor', info)

            block = re.sub('\s|\(.*?\)','',response).upper()
            block = re.sub('\\\\','',block) # Strip \ block delete character
            block = re.sub('%','',block) # Strip % program start/stop character

            # Clear 'System Ok' which accompanies $G reply
            #response = self.serPort.readline().decode('ascii') # python3
            response = self.serPort.readline() # python2.7
            info = response.strip()

            cmds = re.findall(r'[^0-9\.\-]+', block) # Extract block command characters
            nums = re.findall(r'[0-9\.\-]+', block) # Extract block numbers

            for cmd,num in zip(cmds, nums) :
                fnum = float(num)
                if cmd == 'F' :
                    if fnum <= 0:
                        info = 'Please set the default Feed Rate'
                        ok2go = False

            self.postInfo('grblMonitor', info)
            self.update_idletasks()
            return ok2go


#-------------------------------------------------------------------------------
#       PyGrbl_ControlPanel Widget Classes
#-------------------------------------------------------------------------------

# Jog Button Panel
class jogPanel(Frame):
    def __init__(self, master, mainClass, buttons):
        Frame.__init__(self, master = master)

        self.addJButts(mainClass, buttons)

    def addJButts(self, mainClass, buttons):
        r = 0
        for bRow in buttons:
            c = 0
            for bCol in bRow:
                btext = bCol[0]
                motion = bCol[1]
                if btext != "": jogButton(self, mainClass, btext, motion, r, c)
                c += 1
            r += 1

class jogButton(Button):
    def __init__(self, master, mainClass, btext, motion, r, c):
        Button.__init__(self, master = master)

        self.configure(text = btext, command = lambda: mainClass.ButtonHandler(motion))
        self.configure(font = mainClass.JogButtonFont, state = "disabled")
        self.configure(state = "disabled")
        self.grid(row = r, column = c)
        if r == 0: self.grid(pady = (5, 0))
        if c == 0 or c == 3: self.grid(padx = (5, 0))

# rectangular buttons:
class cmdButton(Button):
    def __init__(self, master, mainClass, btext, action, r, c):
        Button.__init__(self, master = master)

        self.configure(text = btext, command = lambda: mainClass.ButtonHandler(action))
        self.configure(width = 8, state = "disabled")
        self.grid(row = r, column = c, padx = 5, pady = 2)

class qryButton(Button):
    def __init__(self, master, mainClass, btext, action, r, c):
        Button.__init__(self, master = master)

        self.configure(text = btext, command = lambda: mainClass.ButtonHandler(action))
        self.configure(width = 10, state = "disabled")
        self.grid(row = r, column = c, padx = 5, pady = 2)

## gCode input buttons:
class keyBar(Frame):
    def __init__(self, master, mainClass, options):
        Frame.__init__(self, master = master)
        self.addButts(mainClass, options)

    def addButts(self, mainClass, options):
        r = 0
        c = 0
        bCount = len(options)
        for b in range(bCount):
            keyButton(self, mainClass, options[b], r, c)
            c+= 1
            
class keyButton(Button):
    def __init__(self, master, mainClass, options, r, c):
        Button.__init__(self, master = master)
        btext = options[0]
        action = options[1]

        self.configure(text = btext, command = lambda: mainClass.ButtonHandler(action))
        self.configure(state = "disabled", width = 2)
        self.grid(row = r, column = c)

# increase/decrease values button bar:
class incDecBar(Frame):
    def __init__(self, master, mainClass, options, var):
        Frame.__init__(self, master = master)
        self.addButtsWLabel(mainClass, options, var)

    def addButtsWLabel(self, mainClass, options, var):
        c = 0
        bCount = len(options)
        for b in range(int(bCount / 2)):
            incDecButt(self, mainClass, options[b], c)
            c += 1

        self.varLabel = Label(self, textvariable = var, width = 5)
        self.varLabel.grid(row = 0, column = c)
        c += 1

        for b in range(int(bCount / 2), bCount):
            incDecButt(self, mainClass, options[b], c)
            c += 1

class incDecButt(Button):
    def __init__(self, master, mainClass, options, c):
        Button.__init__(self, master = master)
        btext = options[0]
        action = options[1]

        self.configure(text = btext, command = lambda:mainClass.ButtonHandler(action))
        self.configure(state = "disabled")
        self.grid(row = 0, column = c)

# combobox
class selectBox(ttk.Combobox):
    def __init__(self, master, mainClass, opt_list, r, c):
        ttk.Combobox.__init__(self, master = master)

        self.configure(values=opt_list)
        self.configure(state = "readonly") # to prevent user typed input
        self.current(0)
        self.grid(row = r, column = c, padx = 5, pady = 5)


#-------------------------------------------------------------------------------
#       Wiimote
#-------------------------------------------------------------------------------

class PyGrbl_Wii(Frame):
    def __init__(self, master, app):
        Frame.__init__(self, master = master)

        ##  WHO AM I ?
        #print(self.winfo_class())  # = 'Frame' !!
        #print(self.__class__.__name__) # = 'PyGrbl_Wii'

        self.app = app
        self.app.apps.append(self.__class__.__name__)
        self.app.wiiState = "Disconnected"

    def wiiConnect(self):
        try:
            mess = "Connecting to your Wiimote. Make sure you are holding buttons 1 + 2!"
            showinfo(title="WiiMote Connection", message = mess)
            self.app.wiiState = self.wiiStart()
            while self.app.wiiState == "Retry":
                self.app.wiiState = self.wiiStart()
            if self.app.wiiState == "Connected":
                if self.app.debugMode > 1: print("wiiConnect: Ok")
                self.readWiiButtons()

        except:
            if self.app.debugMode > 0: print("wiiConnect: Error")

    def wiiStart(self):
        try:
            try:
                self.wii=cwiid.Wiimote("CC:9E:00:CD:96:FC")
                self.wii.rumble = 1
                time.sleep(0.25)
                self.wii.rumble = 0
                self.wii.led = 1
                if self.app.debugMode > 1: print("wiiStart (conn): Ok")
                return "Connected"
            except:
                mess = "Cannot connect to your Wiimote. Run again and make sure you are holding buttons 1 + 2!"
                if askretrycancel(title="WiiMote Connection", message = mess):
                    if self.app.debugMode > 1: print("wiiStart (retry): Ok")
                    return "Retry"
                else:
                    if self.app.debugMode > 1: print("wiiStart (disconn): Ok")
                    return "Disconnected"

        except:
           if self.app.debugMode > 1: print("wiiStart: Error")

    def wiiStop(self):
        try:
            self.wii.rumble = 1
            time.sleep(0.25)
            self.wii.rumble = 0
            self.wii.close()
            self.app.wiiState = "Disconnected"
            if self.app.debugMode > 1: print("wiiStop: Ok")

        except:
            if self.app.debugMode > 1: print("wiiStop: Error")

    def readWiiButtons(self):
        if True:
            if self.app.wiiState == "Connected": # wiiState indicates 'connected'
                try:
                    self.wii.rpt_mode = cwiid.RPT_BTN # check that signal not lost
                except:
                    self.app.wiiState = "Disconnected" # if signal lost, update wiiState
                    return

                #self.wiiBatt = self.wii.state['battery'] # TO DO: put this somewhere more suitable

                buttons = self.wii.state['buttons']
                if buttons:
                    if (buttons - cwiid.BTN_LEFT == 0):
                        self.app.ControlPanel.jogMotor('X-1')
                    elif(buttons - cwiid.BTN_RIGHT == 0):
                        self.app.ControlPanel.jogMotor('X1')
                    elif (buttons - cwiid.BTN_UP == 0):
                        self.app.ControlPanel.jogMotor('Y1')
                    elif (buttons - cwiid.BTN_DOWN == 0):
                        self.app.ControlPanel.jogMotor('Y-1')
                    elif (buttons  - (cwiid.BTN_B + cwiid.BTN_UP) == 0):
                        self.app.ControlPanel.jogMotor('Z1')
                    elif (buttons - (cwiid.BTN_B + cwiid.BTN_DOWN) == 0):
                        self.app.ControlPanel.jogMotor('Z-1')

            self.after(20, self.readWiiButtons)

            if self.app.debugMode > 1: print("readWiiButtons: Ok")
        #except:
            #if self.app.debugMode > 1: print("readWiiButtons: Error")


#-------------------------------------------------------------------------------
#       MAIN
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    screen = "AcerTouch"
    #screen = "10.1"
        
    root = Tk()
    app = PyGrbl_GUI(root)
    app.master.title("PyGrbl Control Panel")

    app.ControlPanel = PyGrbl_ControlPanel(app.mainFrame, app)
    app.wiiMote = PyGrbl_Wii(app.mainFrame, app)
    app.currentApp = app.ControlPanel

    root.mainloop()
