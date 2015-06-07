#!/usr/bin/python2.7

"""
PyGrbl_gCodeChecker

adapted from preGrbl Copyright (c) 2011 Sungeun K. Jeon
version: 20100825 downloaded from GitHub 7 Jan 2015

"""

from Tkinter import *
import re
from copy import deepcopy

from PyGrbl_GUI import *

class PyGrbl_gCodeChecker(Frame):    
    def __init__(self, master, app):
        Frame.__init__(self, master = master)
        
        ##  WHO AM I ?
        #print("Who am I:  " + self.winfo_class())  # = 'Frame' !!
        #print("Who is my parent: " + app.__class__.__name__) # = PyGrbl_GUI
        #print("Who am I:  " + self.__class__.__name__) # = 'PyGrbl_gCodeChecker'
        
        self.app = app
        self.app.servicemenu.entryconfig("gCode Checker", state = "normal")
        self.app.apps.append(self.__class__.__name__)
        self.openFileTrace = self.app.fileOpenFlag.trace_variable('w', self.fileOpenTraceAction)

        self.checkerWaiting = False

        self.ndigits_in = 4 # inch significant digits after '.'
        self.ndigits_mm = 2 # mm significant digits after '.'    
        self.inch2mm = 25.4 # inch to mm conversion scalar

        # Initialize parser state
        self.gc = { 'current_xyz' : [0,0,0], 
           'feed_rate' : 0,         # F0
           'motion_mode' : 'SEEK',  # G00
           'plane_axis' : [0,1,2],  # G17
           'inches_mode' : False,   # G21
           'inverse_feedrate_mode' : False, # G94
           'absolute_mode' : True}  # G90

        self.create_gCodeCheckerWidgets()
        
        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)
        self.grid(column = 0, row = 0, sticky = (N, S, W, E))

    def create_gCodeCheckerWidgets(self):
        if self.app.debugMode > 0:
            status = "Create gCode Checker Widgets"
            print(status)

        self.gCodeCheckerTable = ScrollTable(self, self.app)
        self.gCodeCheckerTable.grid(row = 0, column = 0)

    def fileOpenTraceAction(self, name, index, mode):
        if self.app.fileOpenFlag.get() == True:
            print("File Open Trace Action: File Opened")
            if self.app.currentApp == self.app.gCodeChecker:
                self.check_gCode()
                self.gCodeCheckerTable.fill_STable(self.app.gCodeData)
            elif self.checkerWaiting:
                self.check_gCode()
                self.gCodeCheckerTable.fill_STable(self.app.gCodeData)
                self.checkerWaiting = False                
            else:
                self.checkerWaiting = True
                self.after(100, self.fileOpenTraceAction(name, index, mode))
            self.update_idletasks()
            
        else: # file has been closed
            print("File Open Trace Action: File Closed")
#            for child in self.gCodeCheckerTable.winfo_children():
#                child.destroy()
            self.gCodeCheckerTable.grid_remove()
            self.gCodeCheckerTable.destroy()
            self.update_idletasks()
            self.create_gCodeCheckerWidgets()


    def check_gCode(self):
        if self.app.debugMode > 0: print("Grbl gCodeChecker: Check")

        #print("Check gCode Starting")
        #fileIn = open(filename, 'r')
        self.app.gCodeData = [[], [], [], []] #output for GUI results screen [0] / [1] AND validated code [2]
      
        # Iterate through g-code file
        l_count = 0
        for line in self.app.inFile:
            l_count += 1 # Iterate line counter
            #print("Checking line: " + str(l_count))
            self.app.gCodeData[0].append(line.strip())
            self.done = False
          
            # Strip comments/spaces/tabs/new line and capitalize. Comment MSG not supported.
            block = re.sub('\s|\(.*?\)','',line).upper() 
            block = re.sub('\\\\','',block) # Strip \ block delete character
            block = re.sub('%','',block) # Strip % program start/stop character
          
            if len(block) == 0:  # Ignore empty blocks
                if  len(line.strip()) > 0:
                    response = ['Ok', "None gCode block:  Skipping", ""]
                    self.respond(response)
                    continue

                else:
                    response = ['Ok', "blank line :  Skipping", ""]
                    self.respond(response)
                    continue
              
            else :  # Process valid g-code clean block. Assumes no block delete characters or comments

                # Pass 1
                g_cmd = re.findall(r'[^0-9\.\-]+',block) # Extract block command characters
                g_num = re.findall(r'[0-9\.\-]+',block) # Extract block numbers
              
                # G-code block error checks
                if len(g_cmd) != len(g_num):
                    response = ['Error', "Invalid block. Unbalanced word and values", ""]
                    self.respond(response)
                    continue

                elif 'N' in g_cmd :
                    if g_cmd[0]!='N':
                        response = ["Error", "Line number must be first command in line", ""]
                        self.respond(response)
                        continue

                    elif g_cmd.count('N') > 1:
                        response = ['Error', "More than one line number in block", ""]
                        self.respond(response)
                        continue

                    g_cmd = g_cmd[1:]  # Remove line number word
                    g_num = g_num[1:]
              
                # Initialize block state
                blk = { 'next_action' : 'DEFAULT',
                        'absolute_override' : False,
                        'target_xyz' : deepcopy(self.gc['current_xyz']),
                        'offset_ijk' : [0,0,0],
                        'radius_mode' : False, 
                        'unsupported': [] }

                # Pass 2
                for cmd,num in zip(g_cmd,g_num) :
                    #print("pass 2: " + cmd)
                    if self.done: break
                    fnum = float(num)
                    inum = int(fnum)
                    if cmd == 'G' :
                        if   inum == 0 : self.gc['motion_mode'] = 'SEEK'
                        elif inum == 1 : self.gc['motion_mode'] = 'LINEAR'
                        elif inum == 2 : self.gc['motion_mode'] = 'CW_ARC'
                        elif inum == 3 : self.gc['motion_mode'] = 'CCW_ARC'
                        elif inum == 4 : blk['next_action'] = 'DWELL'
                        elif inum == 17 : self.gc['plane_axis'] = [0,1,2]    # Select XY Plane
                        elif inum == 18 : self.gc['plane_axis'] = [0,2,1]    # Select XZ Plane
                        elif inum == 19 : self.gc['plane_axis'] = [1,2,0]    # Select YZ Plane
                        elif inum == 20 : self.gc['inches_mode'] = True      
                        elif inum == 21 : self.gc['inches_mode'] = False
                        elif inum == [28,30] : blk['next_action'] = 'GO_HOME'
                        elif inum == 53 : blk['absolute_override'] = True
                        elif inum == 80 : self.gc['motion_mode'] = 'MOTION_CANCEL'
                        elif inum == 90 : self.gc['absolute_mode'] = True
                        elif inum == 91 : self.gc['absolute_mode'] = False
                        elif inum == 92 : blk['next_action'] = 'SET_OFFSET'
                        elif inum == 93 : self.gc['inverse_feedrate_mode'] = True
                        elif inum == 94 : self.gc['inverse_feedrate_mode'] = False
                        else :
                            response = ['Error', "Unsupported command " + cmd + str(num), ""]
                            self.respond(response)
                            continue

                    elif cmd == 'M' :
                        if   inum in [0,1] : pass   # Program Pause
                        elif inum in [2,30,60] : pass   # Program Completed
                        elif inum == 3 : pass   # Spindle Direction 1
                        elif inum == 4 : pass   # Spindle Direction -1
                        elif inum == 5 : pass   # Spindle Direction 0
                        else :
                            response = ['Error', "Unsupported command " + cmd + str(num), ""]
                            self.respond(response)
                            continue

                    elif cmd is 'T' : # Tool Number
                        response = ['Ok', "Tool Change command ", ""]
                        self.respond(response)
                  
                if self.done: continue # line complete, exit loop
                
                # Pass 3
                for cmd,num in zip(g_cmd,g_num) :
                    #print("pass 3")
                    if self.done: break
                    fnum = float(num)         
                    if   cmd == 'F' : self.gc['feed_rate'] = self.unit_conv(fnum)   # Feed Rate
                    elif cmd in ['I','J','K'] : blk['offset_ijk'][ord(cmd)-ord('I')] = self.unit_conv(fnum) # Arc Center Offset
                    elif cmd == 'P' : p = fnum  # Misc value parameter
                    elif cmd == 'R' : r = self.unit_conv(fnum); blk['radius_mode'] = True    # Arc Radius Mode
                    elif cmd == 'S' : pass      # Spindle Speed
                    elif cmd in ['X','Y','Z'] : # Target Coordinates
                        if (self.gc['absolute_mode'] | blk['absolute_override']) :
                            blk['target_xyz'][ord(cmd)-ord('X')] = self.unit_conv(fnum)
                        else :
                            blk['target_xyz'][ord(cmd)-ord('X')] += self.unit_conv(fnum)
                    elif cmd not in ['G', 'M', 'T']:
                        response = ['Error', "Unsupported Command " + cmd, ""]
                        self.respond(response)
                        continue

                if self.done: continue # line complete, exit loop

                # Execute actions
                if   blk['next_action'] == 'GO_HOME' : 
                    self.gc['current_xyz'] = deepcopy(blk['target_xyz']) # Update position      
                elif blk['next_action'] == 'SET_OFFSET' : 
                    pass 
                elif blk['next_action'] == 'DWELL' :
                    if p < 0 :
                        response = ['Error', "Dwell time negative", ""]
                        self.respond(response)
                        continue

                else : # 'DEFAULT'
                    if self.gc['motion_mode'] == 'SEEK' : 
                        self.gc['current_xyz'] = deepcopy(blk['target_xyz']) # Update position
                    elif self.gc['motion_mode'] == 'LINEAR' :
                        self.gc['current_xyz'] = deepcopy(blk['target_xyz']) # Update position
                    elif self.gc['motion_mode'] in ['CW_ARC','CCW_ARC'] :
                        axis = self.gc['plane_axis']
                        x = blk['target_xyz'][axis[0]]-self.gc['current_xyz'][axis[0]]
                        y = blk['target_xyz'][axis[1]]-self.gc['current_xyz'][axis[1]]
                        if (x==0 and y==0) :
                            response = ['Error', 'Same target and current XYZ', '']
                            self.respond(response)
                            continue

                out_block = "".join([c+g for (c,g) in zip(g_cmd,g_num)]) 
                if len(out_block) :
                    response = ['Ok', "", out_block]
                    self.respond(response)

        print("Check gCode Complete")
        self.app.inFile.seek(0) # reset inFile cursor to top of file


    def unit_conv(self, val) : # Converts value to mm
        if self.app.debugMode > 1: print("Grbl gCodeChecker: unit_conv")
        if self.gc['inches_mode'] : val *= self.inch2mm
        return(val)

    def fout_conv(self, val) : # Returns converted value as rounded string for output file.
        if self.app.debugMode > 1: print("Grbl gCodeChecker: fout_conv")
        if self.gc['inches_mode'] : return( str(round(val/self.inch2mm,self.ndigits_in)) )
        else : return( str(round(val,self.ndigits_mm)) )

    def respond(self, response):
        if self.app.debugMode > 1: print("Grbl gCodeChecker: Respond")
        
        #result = response[0]
        #comment = response[1]
        #out_block = response[2]
        
        self.app.gCodeData[1].append(response[0]) #result
        self.app.gCodeData[2].append(response[1]) #comment
        self.app.gCodeData[3].append(response[2]) #out_block

        self.done = True
        
        if self.app.debugMode > 1: print("Response: " + comment)


#####
#####
##
## MAIN
##

if __name__ == "__main__":
    root = Tk()

    app = PyGrbl_GUI(root)
    app.master.title("PyGrbl gCode Checker")

    #filename = "/home/pi/PyGrbl Dev/Testing GrblCtrller.nc"
    
    app.gCodeChecker = PyGrbl_gCodeChecker(app.mainFrame, app)
    app.currentApp = app.gCodeChecker

    #myCheckedData = myChecker.check(filename)
    #print(myCheckedData)
    #myChecker.gCodeCheckerTable.fill_STable(myCheckedData)

    root.mainloop()
