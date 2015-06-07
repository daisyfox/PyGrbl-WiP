#!/usr/bin/python3.2

"""
Grbl_Control

"""

from tkinter import *
from tkinter import ttk
import os, sys, glob, serial, time, re

import os.path
from copy import *

import tkinter.font

from PyGrbl_ScrollTable import *

##
#
# DEGUG MODE SETTING
#

debugMode = 0 # 0=None, 1=High Level Only, 2 = Everything

##
#
# GLOBAL VARIABLES
#

#text box font
textboxFont = ("Helvetica", 14)


class Grbl_ControlPanel_App(Frame):

    def __init__(self, master):
        super(Grbl_ControlPanel_App, self).__init__(master)
        self.master.title("Grbl Control Panel App")

        self.debugMode = debugMode
        self.filename = "Selected Job: --- using internal data ---"
        print(self.filename)

        screenWidth = 600
        screenHeight = 300

        self.master.geometry(str(screenWidth) + "x" + str(screenHeight + 30))
        self.grid(column = 0, row = 0)

        mainFrame = Frame(self)
        mainFrame.grid()
        self.ControlPanel = Grbl_ControlPanel(mainFrame, self)
        
        self.ControlPanel.gCodeData =['G21', 'G00Z2', 'G90', 'G00X90Y10', 'G90', 'G01Z0',
                    'G00Z2', 'G91', 'G00X15.3Y1.9', 'G90', 'G01Z0', 'G00Z2',
                    'G91', 'G0X14.7Y4.9', 'G90', 'G1Z0', 'G0Z2', 'G91', 'G0X13.6Y7.6',
                    'G90', 'G1Z0', 'G0Z2', 'G91', 'G0X12.0Y10.0', 'G90', 'G1Z0', 'G0Z2',
                    'G91', 'G0X10.0Y12.0', 'G90', 'G1Z0', 'G0Z2', 'F100']
        



class Grbl_ControlPanel(Frame):
    def __init__(self, master, mainClass):
        Frame.__init__(self, master = master)

        try:
            self.debugMode = mainClass.debugMode
            
        except:
            self.debugMode = 1
            print("debug Exception: Grbl_ControlPanel")
            
        if self.debugMode > 0: print("init Grbl ControlPanel")

        self.create_ControlWidgets()
        #self.state = StringVar() # phase 4 addition
        #self.state.set('')


    def create_ControlWidgets(self):

        ## LEFTSIDE CONTROLS
        
        # USB CONNECTION MANAGER
        self.usbmgr = Frame(self, borderwidth = 2, relief = RIDGE)
        self.usbmgrLabel = Label(self.usbmgr, text = "USB Port")
        self.usbmgrLabel.grid(row = 0, column = 0, sticky = (S, W))

        # usb combobox list
        usbPorts = ['usbports']
        ports = (glob.glob('/dev/tty[A-Za-z]*'))
        for p in ports: usbPorts.append(p)
        self.usbList = selectBox(self.usbmgr, self, usbPorts, 1, 0)
        self.usbList.grid(sticky = W) # additional 'grid' to get columnspan

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
        self.XmYp = jogButton(self.jogmgr, self, "\u25F8", 'XmYp', r, c)
        self.Yp = jogButton(self.jogmgr, self, "\u25B2", 'Yp', r, c + 1)
        self.XpYp = jogButton(self.jogmgr, self, "\u25F9", 'XpYp', r, c + 2)
        self.Zp = jogButton(self.jogmgr, self, "\u25B2", 'Zp', r, c + 3)

        # centre row
        self.Xm = jogButton(self.jogmgr, self, "\u25C0", 'Xm', r + 1, c)
        self.Hm = jogButton(self.jogmgr, self, "\u263C", 'gotoHm', r + 1, c + 1)
        self.Xp = jogButton(self.jogmgr, self, "\u25B6", 'Xp', r + 1, c + 2)

        #Jog stepsize combobox
        jogsizes = ['jogsize', '0', '0.01', '0.05', '0.1', '0.5', '1', '5', '10', '50', '100']
        self.jogsizeList = selectBox(self.jogmgr, self, jogsizes, r + 1, c + 3)
        self.jogsizeList.configure(width = 5)

        # bottom row
        self.XmYm = jogButton(self.jogmgr, self, "\u25FA", 'XmYm', r + 2, c)
        self.Ym = jogButton(self.jogmgr, self, "\u25BC", 'Ym', r + 2, c + 1)
        self.XpYm = jogButton(self.jogmgr, self, "\u25FF", 'XpYm', r + 2, c + 2)
        self.Zm = jogButton(self.jogmgr, self, "\u25BC", 'Zm', r + 2, c + 3)

        self.jogmgr.grid(row = 1, column = 0, ipadx = 5, ipady = 5, sticky = (N, S, W, E))


        # POSITION MANAGER
        r = 0
        self.posmgr = Frame(self, borderwidth = 2, relief = RIDGE)
        self.posmgrLabel = Label(self.posmgr, text = "Tool Position")
        self.posmgrLabel.grid(row = 0, column = 0, sticky = SW)

        r += 1
        rowList = ['M Pos', 'W Pos']
        colList = ['X', 'Y', 'Z']
        self.position = Table(self.posmgr, self, colList, rowList)
        self.position.grid(row = 1, column = 0, columnspan = 3, sticky = (N, S, W, E))

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


    def setWstate(self, widget, state): # set state of individual widget
            widget.configure(state = state)

    def setWCstate(self, frame, widgetType, newState): # set state of class of widgets in parent frame
            for child in frame.winfo_children():
                if child.__class__.__name__ == widgetType:
                    child.configure(state = newState)

#------------------------------------------------------------------------------------
#       Event Handler methods
#------------------------------------------------------------------------------------

    def ButtonHandler(self, request): # button handler - all button commands start here !!!
        if debugMode > 0: print("Button Handler")

        if request in ['XmYp', 'Yp', 'XpYp', 'Xm', 'Xp', 'XmYm', 'Ym', 'XpYm', 'Zp', 'Zm']:
            jog = self.jogsize

        #self.usbConn
        if request == 'connect': self.toggleUSBPort()

        #self.XmYp, self.Yp, self.XpYp, self.Zp
        elif request == 'XmYp': self.jogMotor('X-' + str(jog) + 'Y' + str(jog))
        elif request == 'Yp': self.jogMotor('Y' + str(jog))
        elif request == 'XpYp': self.jogMotor('X' + str(jog) + 'Y' + str(jog))
        elif request == 'Zp': self.jogMotor('Z' + str(jog))

        #self.Xm, self.Hm, self.Xp
        elif request == 'Xm': self.jogMotor('X-' + str(jog))
        elif request == 'gotoHm': print('goto temp home')
        elif request == 'Xp': self.jogMotor('X' + str(jog))

        #self.XmYm, self.Ym, self.XpYm, self.Zm
        elif request == 'XmYm': self.jogMotor('X-' + str(jog) + 'Y-' + str(jog))
        elif request == 'Ym': self.jogMotor('Y-' + str(jog))
        elif request == 'XpYm': self.jogMotor('X' + str(jog) + 'Y-' + str(jog))
        elif request == 'Zm': self.jogMotor('Z-' + str(jog))

        #self.homing, self.unlock, self.sReset, self.hReset
        elif request == 'homing': self.sendPreset('$H')
        elif request == 'unlock': self.sendPreset('$X')  
        elif request == 'sReset': self.reset('soft')
        elif request == 'hReset': self.reset('soft')

        #self.cmdSend
        elif request == 'send': self.sendCommand()

        #self.getStatus (& settings)
        elif request == 'settings': self.sendPreset('$$')
        elif request == 'parameters': self.sendPreset('$#')
        elif request == 'parser': self.sendPreset('$G')
        elif request == 'gMode': self.sendPreset('$C')
        elif request == 'startblk': self.sendPreset('$N')
        elif request == 'status': self.sendPreset('?')

        #self.posMHm, self.posWHm1, self.posWHm2
        elif request == 'gotoMHm': print('goto Machine Home')
        elif request == 'gotoWHm1': print('goto Work Home 1')
        elif request == 'gotoWHm2': print('goto Work Home 2')
        elif request == 'sRun': self.runJob('simple')
        elif request == 'aRun': self.runJob('aggressive')
        elif request == 'hold': self.holdJob()
        elif request == 'stop': self.stopJob()
        

    def optionHandler(self, name):
        if debugMode > 1: print('optionHandler')

        # usb selected
        if name == "usbports":
            self.usbPort = self.usbList.get()
            self.setWstate(self.usbConn, "normal")

        elif name == "jogsize":
            self.jogsize = self.jogsizeList.get()
            if self.usbConn["text"] == "Disconnect": # ie serial connected
                self.setWCstate(self.jogmgr, "jogButton", "normal")

#------------------------------------------------------------------------------------
#       Button Event Action methods
#------------------------------------------------------------------------------------

    def toggleUSBPort(self):
        #print("ToggleUSBPort")
        # print(self.togglePort.cget("bg"))
        #default col #d9d9d9

        if True:
            if self.usbConn["text"] == "Connect":
                self.usbConn.configure(text = "Disconnect", bg = "#ff8080")
                self.serPort = serial.Serial(self.usbPort, baudrate = 115200, timeout = 1)
                self.writeBlock('\r\n\r')
                time.sleep(2)
                self.readResponses()
                self.serPort.flushInput()

                #if self.usbPortOK:
                self.setWCstate(self.cmdmgr, "cmdButton", "normal")
                #self.setWCstate(self.posmgr, "cmdButton", "normal")
                
                try:
                    temp = self.jobmgrLabelVar.get()
                    print(temp)
                    if self.jobmgrLabelVar.get().find('errors') < 0:
                        print("No Errors")
                        self.setWstate(self.runS, "normal")
                        self.setWstate(self.runA, "normal")
                    else:
                        print("Errors")
                        self.setWstate(self.runS, "disabled")
                        self.setWstate(self.runA, "disabled")
                except:
                    print("Toggle USBPort, change jobmgr button state Error")

                try:
                    if self.jogsize:
                        self.setWCstate(self.jogmgr, "jogButton", "normal")
                except:
                    pass

            elif self.usbConn["text"] == "Disconnect":
                #if debugMode: print("Button Text: Disconnect to Connect")
                self.usbConn.configure(text = "Connect", bg = "#d9d9d9", state = "normal")
                self.serPort.close()
                self.usbList.set(value = "")
                self.usbConn.configure(state = "disabled")
                self.setWCstate(self.jogmgr, "jogButton", "disabled")
                self.setWCstate(self.cmdmgr, "cmdButton", "disabled")
                #self.setWCstate(self.posmgr, "cmdButton", "disabled")
                self.setWCstate(self.jobmgr, "cmdButton", "disabled")

        #except:
        #    print("ToggleUSBPort Error")


    def sendPreset(self, preset):
        self.writeBlock(preset)
        time.sleep(2)
        self.readResponses()

              
    def sendCommand(self):
        #if debugMode: print("SendCommand: " + self.commandEntry.get())
        if True:
        #try:
            self.writeBlock(self.cmdEntry.get())
            self.cmdEntry.delete(0, END)
            time.sleep(2)
            self.readResponses()
        #except:
            #print("SendCommand Error")

    def jogMotor(self, action):
        if self.debugMode > 0: print("JogMotor:" + motordir+ self.jogStepsize.get())

        if True:
        #try:
            gCode = "G91 "+action + " G90"
            if self.debugMode > 1: print("gCode: " + gCode)

            block = 'G91 ' + action
            self.writeBlock(block)
            #self.readResponse(True)

            block = 'G90'
            self.writeBlock(block)
            #self.readResponse(True)

        #except:
            #print("jogMotor Error")

    def runJob(self, runType):
        if self.debugMode > 0: print("Run: " + runType)

        ok2go = self.sendInfoRequest('Feedrate')
        
        if ok2go:
            self.setWCstate(self.usbmgr, "cmdButton", "disabled")
            self.setWCstate(self.jogmgr, "jogButton", "disabled")
            self.setWCstate(self.cmdmgr, "cmdButton", "disabled")
            self.setWCstate(self.posmgr, "cmdButton", "disabled")
            self.setWstate(self.runS, "disabled")
            self.setWstate(self.runA, "disabled")
            self.setWstate(self.hold, "normal")
            self.setWstate(self.stop, "normal")
            self.setWstate(self.sReset, "normal")
            self.update_idletasks()

            self.holdState = False
            self.stopState = False
            self.doNextState = True
            self.doneState = False

            # clear input buffer so that response stream is not corrupted
            # by late responses to earlier sends
            self.serPort.flushInput()

            if runType == "simple": self.simpleStream(self.gCodeData)
            else: self.aggressiveStream(self.gCodeData)


    def holdJob(self):
        self.holdState = not self.holdState

        if self.hold['text'] == 'Hold':
            self.hold['text'] = 'Resume'
            self.postInfo('grblStatus', 'Sending:  Hold')
            self.update_idletasks()
            self.sendPreset('!')
        else:
            self.hold['text'] = 'Hold'
            self.postInfo('grblStatus', 'Sending:  Resume')
            self.update_idletasks()
            self.sendPreset('~')

        self.update_idletasks()

    def stopJob(self):
        self.stopState = True
        self.doneState = True
        self.postInfo('grblStatus', 'Sending:  STOP !')
        self.update_idletasks()
        self.sendPreset('!')


    def reset(self, resetType): # different for soft/hard 
        self.doneState = True
        self.sendPreset('!') # feedhold will control deceleration
        self.sendPreset('\x18')
        self.update_idletasks()


#------------------------------------------------------------------------------------
#       Stream gCode using Simple call response method
#------------------------------------------------------------------------------------

    def simpleStream(self, gCodeList):
        print("simpleStream")
        # Must be used if sending streaming settings (read below)

        # Send gCode by simple call-response streaming method. Settings must be streamed
        # in this manner since the EEPROM accessing cycles shut-off the serial interrupt.

        self.l_count = 0
        self.l_block = ''
        self.gCodeList = gCodeList

        #self.simpleForLoop()
        self.simpleAfterLoop()


    def simpleForLoop(self):  ## doesn't allow interrupts to stream loop
        for line in self.gCodeList:
            self.l_count += 1
            self.l_block = line.strip()
            info = 'SND: ' + str(self.l_count) + ':' + self.l_block
            self.postInfo('grblStatus', info)
            self.writeBlock(self.l_block)

            #check if responses available !!!
            g_out =  self.readResponse()
            self.postInfo('grblStatus', g_out)

        self.postInfo('grblStatus', 'Done!!')

        self.setWCstate(self.usbmgr, "cmdButton", "normal")
        self.setWCstate(self.jogmgr, "jogButton", "normal")
        self.setWCstate(self.cmdmgr, "cmdButton", "normal")
        self.setWCstate(self.posmgr, "cmdButton", "normal")
        self.setWstate(self.runS, "normal")
        self.setWstate(self.runA, "normal")
        self.setWstate(self.hold, "disabled")
        self.setWstate(self.stop, "disabled")


    def simpleAfterLoop(self):  ## allows interrupts to stream loop
        doNextFlag = not (self.holdState or self.stopState)

        if doNextFlag:
            line = self.gCodeList[self.l_count]
            self.l_count += 1
            self.l_block = line.strip()
            self.writeBlock(self.l_block)
            info = 'SND: ' + str(self.l_count) + ':' + self.l_block
            self.postInfo('grblStatus', info)

            #check if responses available !!!
            g_out =  self.readResponse()
            self.postInfo('grblStatus', g_out)

        if self.l_count < len(self.gCodeList) and not self.stopState:
            self.after(100, self.simpleAfterLoop) # schedule next iteration of the loop
        else:
            self.doneState = True

        if self.doneState:
            self.postInfo('grblStatus', 'Done!!')
            
            self.setWCstate(self.usbmgr, "cmdButton", "normal")
            self.setWCstate(self.jogmgr, "jogButton", "normal")
            self.setWCstate(self.cmdmgr, "cmdButton", "normal")
            self.setWCstate(self.posmgr, "cmdButton", "normal")
            self.setWstate(self.runS, "normal")
            self.setWstate(self.runA, "normal")
            self.setWstate(self.hold, "disabled")
            self.setWstate(self.stop, "disabled")



#------------------------------------------------------------------------------------
#       Stream gCode using 'Aggressive Buffer' method
#------------------------------------------------------------------------------------

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
        #self.aggForLoopSend()
        self.aggAfterLoopSend()

        # Wait for remaining responses
        #self.aggForLoopRec()
        self.aggAfterLoopRec()
        
        self.postInfo('grblStatus', 'Done !!')  


    def aggForLoopSend(self):
        
        for line in self.gCodeList:
            self.l_count += 1
            self.l_block = line.strip()
            self.c_line.append(len(self.l_block)+1)
            
            #while buffer full and waiting for response WAIT !
            while sum(self.c_line) >= self.BUFFER_SIZE - 1 or self.serPort.inWaiting() :
                out_temp = self.readResponse()
                if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
                    self.postInfo('grblStatus', "Debug:  ")
                    self.postInfo('grblStatus', out_temp)
                else :
                    grbl_out = out_temp
                    self.g_count += 1
                    del self.c_line[0]

                    self.postInfo('grblStatus', "REC: " + str(self.g_count) + " : " + grbl_out)
                    
            # once space available in buffer add next line
            self.writeBlock(self.l_block)
            self.postInfo('grblStatus', "SND: " + str(self.l_count) + " : " + self.l_block)
            self.postInfo('grblStatus', "BUF: " + str(sum(self.c_line)))


    def aggForLoopRec(self): # collect the remaining responses
        
        print(self.c_line, sum(self.c_line))
        while sum(self.c_line) > 0 or self.serPort.inWaiting():
            out_temp = self.readResponse()
            if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
                response = "Debug:  " + out_temp
                self.postInfo('grblStatus', response)
                print(response)
            else :
                grbl_out = out_temp
                self.g_count += 1
                del self.c_line[0]

                self.postInfo('grblStatus', "REC: " + str(self.g_count) + " : " + grbl_out)
                self.postInfo('grblStatus', "BUF: " + str(sum(self.c_line)))

        self.postInfo('grblStatus', 'Done!!')

        self.setWCstate(self.usbmgr, "cmdButton", "normal")
        self.setWCstate(self.jogmgr, "jogButton", "normal")
        self.setWCstate(self.cmdmgr, "cmdButton", "normal")
        self.setWCstate(self.posmgr, "cmdButton", "normal")
        self.setWstate(self.runS, "normal")
        self.setWstate(self.runA, "normal")
        self.setWstate(self.hold, "disabled")
        self.setWstate(self.stop, "disabled")


    def aggAfterLoopSend(self):
        doNextFlag = not (self.holdState or self.stopState)

        if doNextFlag:
            line = self.gCodeList[self.l_count]
            self.l_count += 1
            self.l_block = line.strip()
            self.c_line.append(len(self.l_block)+1)
            
            #while buffer full and waiting for response WAIT !
            while sum(self.c_line) >= self.BUFFER_SIZE - 1 or self.serPort.inWaiting() :
                out_temp = self.readResponse()
                if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
                    self.postInfo('grblStatus', "Debug:  ")
                    self.postInfo('grblStatus', out_temp)
                else :
                    grbl_out = out_temp
                    self.g_count += 1
                    del self.c_line[0]

                    self.postInfo('grblStatus', "REC: " + str(self.g_count) + " : " + grbl_out)
                    
            # once space available in buffer add next line
            self.writeBlock(self.l_block)
            self.postInfo('grblStatus', "SND: " + str(self.l_count) + " : " + self.l_block)
            self.postInfo('grblStatus', "BUF: " + str(sum(self.c_line)))
            
        if self.l_count < len(self.gCodeList) and not self.stopState:
            self.after(100, self.aggAfterLoopSend) # schedule next iteration of the loop


    def aggAfterLoopRec(self): # collect the remaining responses        
        doNextFlag = not (self.holdState or self.stopState)

        if doNextFlag:
            if sum(self.c_line) > 0 or self.serPort.inWaiting():
                out_temp = self.readResponse()
                if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
                    response = "Debug:  " + out_temp
                    self.postInfo('grblStatus', response)
                    print(response)
                else :
                    grbl_out = out_temp
                    self.g_count += 1
                    del self.c_line[0]

                    self.postInfo('grblStatus', "REC: " + str(self.g_count) + " : " + grbl_out)
                    self.postInfo('grblStatus', "BUF: " + str(sum(self.c_line)))

        if self.g_count < len(self.gCodeList) and not self.stopState:
            self.after(100, self.aggAfterLoopRec) # schedule next iteration of the loop
        else:
            self.doneState = True

        if self.doneState:
            self.postInfo('grblStatus', 'Done!!')
            self.setWCstate(self.usbmgr, "cmdButton", "normal")
            self.setWCstate(self.jogmgr, "jogButton", "normal")
            self.setWCstate(self.cmdmgr, "cmdButton", "normal")
            self.setWCstate(self.posmgr, "cmdButton", "normal")
            self.setWstate(self.runS, "normal")
            self.setWstate(self.runA, "normal")
            self.setWstate(self.hold, "disabled")
            self.setWstate(self.stop, "disabled")


#------------------------------------------------------------------------------------
#       Read / Write methods
#------------------------------------------------------------------------------------

    def writeBlock(self, block):
        if True:
        #try:
            gCode_block = bytes(block + '\n', 'UTF-8')
            self.serPort.write(gCode_block)

        #except:
            #print("WriteBlock Error")
    
    def readResponses(self):
        if debugMode > 0: print("readResponses")

        response = self.serPort.readline().decode('ascii')
        while response:
            print(response.strip())
            self.postInfo('grblStatus', response.strip())
            response = self.serPort.readline().decode('ascii')
                    
    def readResponse(self):
        if debugMode > -1: print("readResponse")
        response = self.serPort.readline().decode('ascii')
        return response.strip()

    def postInfo(self, postBoard, info):
        if self.debugMode > 3: print("Post Info")
        if postBoard == 'grblStatus':
            self.grblStatus.configure(state = "normal")
            self.grblStatus.insert(END, info.strip() + '\n')
            self.update_idletasks()
            self.grblStatus.see(END)
            self.grblStatus.configure(state = "disabled")

    def sendInfoRequest(self, request):
        if self.debugMode > 0: print('sendInfoRequest')
        ok2go = True
        info = 'ok'
        
        if request == 'Feedrate':
            self.writeBlock('$G')
            time.sleep(2)

            # $G reply
            response = self.serPort.readline().decode('ascii')
            info = response.strip()
            self.postInfo('grblStatus', info)
            
            block = re.sub('\s|\(.*?\)','',response).upper() 
            block = re.sub('\\\\','',block) # Strip \ block delete character
            block = re.sub('%','',block) # Strip % program start/stop character

            # Clear 'System Ok' which accompanies $G reply
            response = self.serPort.readline().decode('ascii')
            info = response.strip()
            
            cmds = re.findall(r'[^0-9\.\-]+', block) # Extract block command characters
            nums = re.findall(r'[0-9\.\-]+', block) # Extract block numbers

            for cmd,num in zip(cmds, nums) :
                fnum = float(num)
                if cmd == 'F' :
                    if fnum <= 0:
                        info = 'Please set the default Feed Rate'
                        ok2go = False

        self.postInfo('grblStatus', info) 
        self.update_idletasks()
        return ok2go

#------------------------------------------------------------------------------------
#       Widgets
#------------------------------------------------------------------------------------

# combobox for: USB port, Jog stepsize
class selectBox(ttk.Combobox):
    def __init__(self, master, mainClass, opt_list, r, c):
        ttk.Combobox.__init__(self, master = master)

        self.optSelected = StringVar()
        self.configure(values=opt_list[1:], textvariable=self.optSelected, font = (12))
        self.configure(state = "readonly") # to prevent user typed input
        self.bind("<<ComboboxSelected>>", lambda *args: mainClass.optionHandler(opt_list[0]))
        self.grid(row = r, column = c, padx = 5, pady = 5)

# square buttons: dir arrow icons
class jogButton(Button):
    def __init__(self, master, mainClass, btext, motion, r, c):
    #def __init__(self, master, icon, motion, r, c):
        Button.__init__(self, master = master)

        self.configure(text = btext, command = lambda: mainClass.ButtonHandler(motion))
        self.configure(font = tkinter.font.Font(size = 28))
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



#####
#####
##
## MAIN
##

if __name__ == "__main__":
    root = Tk()
    app = Grbl_ControlPanel_App(root)
    root.mainloop()
