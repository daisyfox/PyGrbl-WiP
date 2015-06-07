#!/usr/bin/python2.7

"""
Scroll_Table

"""

from Tkinter import *
#from tkinter import ttk
#import tkinter.font

import time

class ScrollTable(Frame):
    def __init__(self, master, mainClass): # mainClass = self.app from gCodeChecker
        Frame.__init__(self, master = master)
        
        self.mainClass = mainClass
        self.debugMode = self.mainClass.debugMode

        ##  WHO AM I ?
        #print("Who am I:  " + self.mainClass.winfo_class())  # = 'Frame' !!
        #print("Who is my main parent: " + self.mainClass.__class__.__name__) # = PyGrbl_GUI
        #print("Who am I:  " + self.__class__.__name__) # = 'ScrollTable'

        self.width = self.mainClass.screenWidth - 30 # TO DO Check scroll width
        self.height = self.mainClass.screenHeight - 100 # TO DO Check status bar height
            
        if self.debugMode > 0: print("init ScrollTable")
        
        self.tablecols = ['line', 'gCode IN', 'Result', 'Comment', 'gCode OUT']
        #self.tablerows = []

        self.build_table_canvas()
        self.grid()

    def build_table_canvas(self):
        self.canvas = Canvas(self, width = self.width, height = self.height)
        self.canvas.grid()
        self.table = Table(self.canvas, self, self.tablecols)

        xscrollbar=Scrollbar(self, orient=HORIZONTAL, width = 15)
        xscrollbar.grid(row = 1, column = 0, sticky=(W,E))
        yscrollbar=Scrollbar(self, orient=VERTICAL, width = 15)
        yscrollbar.grid(row = 0, column = 1, sticky=(N, S))
        
        self.canvas.configure(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
        xscrollbar.configure(command=self.canvas.xview)
        yscrollbar.configure(command=self.canvas.yview)

        self.canvas.create_window((0,0), window=self.table, anchor ='nw')

        self.canvas.bind_all("<Button-4>", self.on_MWheel)
        self.canvas.bind_all("<Button-5>", self.on_MWheel)
        

    def on_MWheel(self, event):
        if self.debugMode > 1: print("ScrollTable: onMWheel")
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        if event.num == 5:
            self.canvas.yview_scroll(1, "units")
            
    def fill_STable(self, data = []):
        if self.debugMode > 0: print("ScrollTable: fill_STable")
        if self.debugMode > 2: print(data)
        self.table.fill_Table(data)
        self.update_idletasks()

        #reset scroll region
        print(self.canvas.winfo_reqheight())
        self.canvas.configure(scrollregion = (0, 0, 2200, 42000)) #self.canvas.bbox('all'))
        print(self.canvas.bbox('all'))

#    def clear_STable(self):
#        self.table.clear_Table()


class Table(Frame):
    def __init__(self, master, mainClass, colList, rowList = []):
        self.mainClass = mainClass
        #if self.mainClass.debugMode > 1: print("init Table")
        
        self.cols = colList
        self.colList = colList
        self.rows = rowList
        self.rowList = rowList
        
        Frame.__init__(self, master = master)
        self.config(padx=10, pady=10)
        self.grid()
        self.make_header()
        self.update_idletasks()


    def fill_Table(self, data = []):
        if self.mainClass.debugMode > 0: print("Table: fill_Table")
##        if self.mainClass.debugMode > 2:
##            print(data)
##            print(len(data[0]))

        dataCols = len(self.colList) - 1
        dataRows = len(data[0])

        statusbarOwner = self.mainClass.mainClass
        statusStr = " : checking gCode file . . ."

        for r in range(dataRows):
            TableEntry(self, 0, r + 1, str(r +1)) # add row number to the scrolltable
            for c in range(dataCols):
                TableEntry(self, c + 1, r + 1, data[c][r]) # add data columns to the scrolltable
        statusStr = " : gCode file check complete"
        statusbarOwner.statusbarText.set(statusbarOwner.statusbarList[0] + statusStr)
        

    def fill_TableV(self, varList = []):
##        if self.mainClass.debugMode > 0: print("Table: fill_Table")
##        if self.mainClass.debugMode > 2:
##            print(data)
##            print(len(data[0]))

        dataCols = len(varList)
        dataRows = len(varList[0])

        for r in range(dataRows):
            for c in range(dataCols):
                TableEntryV(self, c + 1 , r + 1, varList[c][r])
                self.update_idletasks()


#    def clear_Table(self):
#        for child in self.winfo_children():
#            if child.__class__.__name__ == "TableEntry":
#                child.destroy()

    #def setWCstate(self, frame, widgetType, newState): # set state of class of widgets in parent frame
    #        for child in frame.winfo_children():
    #            if child.__class__.__name__ == widgetType:
    #                child.configure(state = newState)

 
    def make_header(self):
        #if self.app.debugMode > 0: print("Table: make_header")

        for c, label in enumerate(self.cols):
            if self.rowList:
                TableLabel(self, c+1, 0, label)
            else:
                TableLabel(self, c, 0, label)

        if self.rowList:
            for r, label in enumerate(self.rows):
                TableLabel(self, 0, r+1, label)

        #else:
            #for r in range(0, len(data[0])):
                #TableLabel(self, 0, r+1, str(r +1))

            
class TableLabel(Label):
    def __init__(self, master, col, row, dataItem):
        #print("TableLabel")
        
        Label.__init__(self, master = master)
        self.config(text = dataItem, anchor = 'w', width = len(dataItem) + 2, relief = FLAT,
                    disabledforeground = "Black", state = "disabled")
        self.grid(column=col, row=row, sticky = 'w')


class TableEntry(Label): # TO DO: amend so this completes full row not just single entry?
    def __init__(self, master, c, r, dataItem):
            
        #if app.debugMode > 1: print("init TableEntry")
        #if app.debugMode > 1: print(dataItem)

        Label.__init__(self, master=master)
        
        if c == 2:
            if dataItem == "Ok": colour = "dark green"
            elif dataItem == "Error": colour = "red4"
        else: colour = "Black"

        self.config(text= dataItem, relief = 'flat', anchor = 'w', disabledforeground = colour,
                    state = "disabled")
        self.grid(column=c, row=r, padx = 0, pady = 0, sticky = 'w')
        self.update_idletasks()
        
        #except:
            #print("Table: TableEntry Error")

class TableEntryV(Label):  ## TO DO:  make this do full rows so highlight easier to apply
    def __init__(self, master, c, r, var):
            
        #if app.debugMode > 1: print("init TableEntry")
        #if app.debugMode > 1: print(dataItem)

        Label.__init__(self, master=master)
        self.config(textvariable = var, relief = 'flat', width = 6)
        self.grid(column=c, row=r, padx = 0, pady = 0, sticky = 'w')
            
        #except:
            #print("Table: TableEntry Error")
