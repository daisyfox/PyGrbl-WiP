#!/usr/bin/python2.7

"""
Grbl_Communicator

"""

from Tkinter import *
import ttk
import serial, re, glob

from PyGrbl_GUI import *

class PyGrbl_Communicator(Frame):
    def __init__(self, master, app):
        Frame.__init__(self, master = master)

        ##  WHO AM I ?
        #print("Who am I:  " + self.winfo_class())  # = 'Frame' !!
        #print("Who is my parent: " + app.__class__.__name__) # = PyGrbl_GUI
        #print("Who am I:  " + self.__class__.__name__) # = 'PyGrbl_ControlPanel'

        self.app = app
        self.app.apps.append(self.__class__.__name__)
        self.filename = "Selected Job: --- using internal data ---"
        
        self.create_CommWidgets()
        
        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)
        self.grid(column = 0, row = 0, sticky = (N, S, W, E))

        self.serPort = ''
        self.waitingFlag = BooleanVar()
        self.waitingFlag.set(False)
        
        self.sender = PyGrbl_Sender(self, self.app, self)
        self.receiver = PyGrbl_Receiver(self, self.app, self)
        self.streamer = PyGrbl_Streamer(self, self.app, self)

        # create a variable trace on sender.sentBlockFlag to start receiver watching for responses
        self.sender.sentBlockFlag.trace_variable('w', self.receiver.blockSentTraceAction)

        # create a variable trace on receiver recdBlockFlag to alert sender (in case of further sends required)
        #self.receiver.recdBlockFlag.trace_variable('w', self.XXX.recdBlockTraceAction)

        # create variable traces for updating user feedback ('monitors')
        #self.receiver.recdBlockFlag.trace_variable('w', self.recdBlockTraceAction)
        #self.receiver.recdEndBlockFlag.trace_variable('w', self.endRecdBlockTraceAction)
        self.receiver.grblWelcomeRecdFlag.trace_variable('w', self.grblWelcomeRecdTraceAction)
        self.receiver.gcodeOkRecdFlag.trace_variable('w', self.gcodeOkRecdTraceAction)
        

    def create_CommWidgets(self):
        r = 0
        c = 0
        # Connect
        self.grblConn = Button(self, text = "Connect\nGrbl", command = self.toggleUSBPort)
        self.grblConn.grid(row = r, column = c, rowspan = 2, padx = 5, pady = 5)

        # USB Port
        Label(self, text = "Select USB Port: ").grid(row = r, column = c + 1, sticky = E)
        self.usbPorts = ['/dev/ttyUSB0']
        self.usbList = ttk.Combobox(self, values = self.usbPorts)
        self.usbList.current(0)
        self.usbList.grid(row = r, column = c + 2, padx = 10, sticky = (W, E)) # additional 'grid' to get columnspan

        Button(self, text = "Refresh", command = self.refreshUSBList).grid(row = r, column = c + 3, padx = 10, sticky = W)

        Button(self, text = "Run Job\nSimple", command = self.streamS).grid(row = r, column = c + 4, rowspan = 2, padx = 10, pady = 5)
        Button(self, text = "Run Job\nAggressive", command = self.streamA).grid(row = r, column = c + 5, rowspan = 2, padx = 10, pady = 5)

        # MONITOR
        r += 1
        Label(self, text = "Command:").grid(row = r, column = c + 1, sticky = E)
        self.cmdEntry = Entry(self, width = 20)
        self.cmdEntry.grid(row = r, column = c + 2, padx = 10, sticky = (W, E))
        self.cmdSendM = Button(self, text = "Send", command = self.sendCmd).grid(row = r,
                                                                                 column = c + 3, padx = 10, pady = 5, sticky = W)

        r += 1
        self.grblMonitor = ScrolledText(self, width = 12, height = 12, state = "disabled")
        self.grblMonitor.grid(row = r, column = 0, columnspan = 4, sticky = (N, S, W, E))
        
        self.grblMonitor2 = ScrolledText(self, width = 12, height = 12, state = "disabled")
        self.grblMonitor2.grid(row = r, column = 4, columnspan = 3, sticky = (N, S, W, E))
        
        self.rowconfigure(r, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(6, weight = 1)

    def todo(self): # placeholder during development
        pass

    def printChildList(self, widget):
        for child in widget.winfo_children():
            if child.winfo_children():
                self.printChildList(child)
            else:
                print(child.__class__.__name__)

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

        if True:
            if self.grblConn["text"] == "Connect\nGrbl":
                if True:
                    self.usbPort = self.usbList.get()
                    #self.serPort = serial.Serial("/dev/ttyACM0", baudrate = 115200, timeout = 1)
                    self.serPort = serial.Serial(self.usbPort, baudrate = 115200, timeout = 2)
                    time.sleep(2)
                    self.postInfo('grblMonitor', '--> \r\n')
                    self.waitingFlag.set(True)
                    self.sender.sendBlock('\r\n') # should trigger 'receiver'
                    self.grblConn.configure(text = "Disconnect\nGrbl", bg = "#bdcbf6")
                    self.app.statusbarText.set("System Status: Grbl Connected")
                    #self.checkGrblStatus()
                    if self.app.debugMode > 1: print("Serial Connect: Ok")
                #except:
                    #print("Serial Connect: Error")
                    #self.app.statusbarText.set("System Status: Unable to Connect Grbl")

            elif self.grblConn["text"] == "Disconnect\nGrbl":
                if True:
                    self.serPort.close()
                    #self.grblConnFlag.set(False)
                    self.grblConn.configure(text = "Connect\nGrbl", bg = "#d9d9d9", state = "normal")
                    self.app.statusbarText.set("System Status: Grbl Disconnected")
                    if self.app.debugMode > 1: print("Serial Disconnect:Ok")
                #except:
                    #print("Serial Disconnect: Error")
                    #self.app.statusbarText.set("System Status: Grbl Not Responding")

        #except:
            #print("ToggleUSBPort Error")
            #self.app.statusbarText.set("System Status: USB port / Grbl not responding")

    def streamS(self):
        self.gCodeList = ['X10', 'Y10', 'X20', 'Y20']
        self.streamer.simpleStream(self.gCodeList)

    def streamA(self):
        pass


#-------------------------------------------------------------------------------
#       Send / Receive methods
#-------------------------------------------------------------------------------

    def sendCmd(self):
        cmd = self.cmdEntry.get() + '\n'
        postBoard = 'grblMonitor'
        self.postInfo(postBoard, '--> ' + cmd)
        self.waitingFlag.set(True)
        self.sender.sendBlock(cmd)
        self.cmdEntry.delete(0, END)
            
##    def recdBlockTraceAction(self, varName, index, mode):
##        if self.getvar(name = varName) == True:
##            postBoard = 'grblMonitor'
##            info = self.receiver.responseList[-1]
##        
##    def endRecdBlockTraceAction(self, varName, index, mode):
##        pass
##        if self.getvar(name = varName) == True:
##            # TO DO: responseList[-1] to identify postBoard
##            responder = self.receiver.responseList[-1]
##            if responder.find('gCode') >= 0:
##                postBoard = 'grblMonitor2'
##            else:
##                postBoard = 'grblMonitor'
##            for info in self.receiver.responseList:
##                self.postInfo(postBoard, '<-- ' + info)

    def grblWelcomeRecdTraceAction(self, varName, index, mode):
        if self.getvar(name = varName) == True:
            if self.waitingFlag.get() == True:
                self.waitingFlag.set(False)
                for info in self.receiver.responseList:
                    self.postInfo('grblMonitor', '<-- ' + info)
                self.receiver.responseList = []

    def gcodeOkRecdTraceAction(self, varName, index, mode):
        if self.getvar(name = varName) == True:
            if self.waitingFlag.get() == True:
                self.postInfo('grblMonitor', '<-- gCode ok')
                self.receiver.responseList.remove('gCode ok')
                self.waitingFlag.set(False)
                self.receiver.gcodeOkRecdFlag.set(False)
                
    def postInfo(self, postBoard, info):
        if self.app.debugMode > 1: print("Post Info")

        if postBoard == 'qryMonitor':
            monitor = self.qryMonitor
        elif postBoard == 'cmdMonitor':
            monitor = self.cmdMonitor
        elif postBoard == 'jogMonitor':
            monitor = self.jogMonitor
        elif postBoard == 'grblMonitor2':
            monitor = self.grblMonitor2
        else: monitor = self.grblMonitor
            
        monitor.configure(state = "normal")
        monitor.insert(END, info.strip() + '\n')
        self.update_idletasks()
        monitor.see(END)
        monitor.configure(state = "disabled")


#-------------------------------------------------------------------------------
#       PyGrbl_Streamer
#-------------------------------------------------------------------------------

class PyGrbl_Streamer(Frame):
    def __init__(self, master, app, parent):
        Frame.__init__(self, master = master)

        ##  WHO AM I ?
        #print(self.winfo_class())  # = 'Frame' !!
        #print(self.__class__.__name__) # = 'PyGrbl_Streamer'

        self.app = app
        self.app.apps.append(self.__class__.__name__)
        self.parent = parent
        
        self.sender = self.parent.sender
        self.receiver = self.parent.receiver
        self.receiver.gcodeOkRecdFlag.trace_variable('w', self.gcodeOkRecdTraceAction)

        self.waitingFlag = BooleanVar()
        self.waitingFlag.set(False)

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
        print(self.gCodeList)
        self.waitingFlag = BooleanVar()
        self.postBoard = 'grblMonitor2'

        self.simpleSend()

    def simpleSend(self):  ## allows interrupts to stream loop
        doNextFlag = True # not (self.holdJobFlag.get() or self.stopJobFlag.get())

        if doNextFlag:
            line = self.gCodeList[self.l_count]
            self.l_count += 1
            self.l_block = line.strip()
            print(self.l_block)
            self.parent.postInfo(self.postBoard, '--> ' + self.l_block)
            self.waitingFlag.set(True)
            self.sender.sendBlock(self.l_block + '\n')

    def gcodeOkRecdTraceAction(self, varName, index, mode):
        if self.parent.getvar(name = varName) == True:
            if self.waitingFlag.get() == True:
                self.waitingFlag.set(False)
                self.receiver.gcodeOkRecdFlag.set(False)
                self.parent.postInfo(self.postBoard, '<-- gCode ok')
                #del self.receiver.responseList[self.receiver.responseList.index('gCode ok')]
                if self.l_count < len(self.gCodeList):
                    print('send next')
                    self.simpleSend()
                else:
                    #self.jobStreamFlag.set(True)
                    #self.checkGrblStatus()
                    pass


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
#       PyGrbl_Sender
#-------------------------------------------------------------------------------

class PyGrbl_Sender(Frame):
    def __init__(self, master, app, parent):
        Frame.__init__(self, master = master)

        ##  WHO AM I ?
        #print(self.winfo_class())  # = 'Frame' !!
        #print(self.__class__.__name__) # = 'PyGrbl_Sender'

        self.app = app
        self.app.apps.append(self.__class__.__name__)
        self.parent = parent

        self.sentBlockFlag = BooleanVar()

    def sendBlock(self, gCode_block):
        if True:
            self.parent.serPort.write(gCode_block)
            self.sentBlockFlag.set(True)

        #except:
            #print("sendBlock: Error")

    
#-------------------------------------------------------------------------------
#       PyGrbl_Receiver
#-------------------------------------------------------------------------------

class PyGrbl_Receiver(Frame):
    def __init__(self, master, app, parent):
        Frame.__init__(self, master = master)

        ##  WHO AM I ?
        #print(self.winfo_class())  # = 'Frame' !!
        #print(self.__class__.__name__) # = 'PyGrbl_Receiver'

        self.app = app
        self.app.apps.append(self.__class__.__name__)
        
        self.parent = parent

        self.waitingCount = 0 # count of 'sends' waiting a complete response
        self.responseList = []
        #self.recdBlockFlag = BooleanVar()
        #self.recdBlockFlag.set(False)
        self.recdEndBlockFlag = BooleanVar()
        self.recdEndBlockFlag.set(False)
        self.grblWelcomeRecdFlag = BooleanVar()
        self.grblWelcomeRecdFlag.set(False)
        self.gcodeOkRecdFlag = BooleanVar()
        self.gcodeOkRecdFlag.set(False)
        

    def blockSentTraceAction(self, varName, index, mode):
        if self.parent.getvar(name = varName) == True:
            self.waitingCount += 1
            self.waitForResponse()

    def waitForResponse(self):
        #response = self.serPort.readline().decode('ascii') # python3
        response = self.parent.serPort.readline() # python2.7
        if response:
            self.responseList.append(response.strip())
            #self.recdBlockFlag.set(True)
            if response.find('ok') >= 0 or response.find('Grbl 0.9g') >= 0:
                if response.find('Grbl 0.9g') >= 0:
                    self.grblWelcomeRecdFlag.set(True)
                    self.parent.serPort.flushInput() # since all expected responses have been recd
                if response.find('gCode ok') >= 0: self.gcodeOkRecdFlag.set(True)
                self.recdEndBlockFlag.set(True)
                self.waitingCount -= 1

        if self.recdEndBlockFlag.get() == False or self.waitingCount > 0:
            self.recdEndBlockFlag.set(False)
            self.after(200, self.waitForResponse)
        else:
            #self.recdBlockFlag.set(False)
            self.recdEndBlockFlag.set(False)
            

#-------------------------------------------------------------------------------
#       MAIN
#-------------------------------------------------------------------------------

if __name__ == "__main__":

    root = Tk()
    app = PyGrbl_GUI(root)
    app.master.title("PyGrbl Communicator")

    app.Communicator = PyGrbl_Communicator(app.mainFrame, app)
    app.currentApp = app.Communicator

    root.mainloop()
