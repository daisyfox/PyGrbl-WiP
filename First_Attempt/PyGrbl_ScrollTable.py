#!/usr/bin/python3.2

"""
Scroll_Table

"""

from tkinter import *
from tkinter import ttk
import tkinter.font

import time

##
# DEGUG MODE SETTING
#

debugMode = 1 # 0=None, 1=High Level Only, 2 = Everything


class ScrollTableApp(Frame):
    def __init__(self, master, data = []):
        super(ScrollTableApp, self).__init__(master)
        self.master.title("Scroll Table App")

        self.debugMode = debugMode

        self.screenWidth = 600
        self.screenHeight = 300 - 30

        self.master.geometry(str(self.screenWidth) + "x" + str(self.screenHeight + 30))
        self.grid(column = 0, row = 0)
        
        mainFrame = Frame(self)
        mainFrame.grid()
        self.STable = ScrollTable(mainFrame, self)
        self.STable.grid()
        

class ScrollTable(Frame):
    def __init__(self, master, mainClass):
        Frame.__init__(self, master = master)

        try:
            self.debugMode = mainClass.debugMode
        except:
            self.debugMode = 1
            print("debug Exception: Scroll Table")
            
        if self.debugMode > 0: print("init ScrollTable")
        
        ##
        #
        # CONSTANTS AND VARIABLE DEFAULT VALUES
        #

        wpadx = 5
        wpady = 5

        #widget font

        #text box font
        textboxFont = ("Helvetica", 14)

        tablecols = ['line', 'gCode IN', 'Result', 'Comment', 'gCode OUT']
        tablerows = []

        self.canvas = Canvas(self, width = mainClass.screenWidth - 20,
                                         height = mainClass.screenHeight - 20)
        self.canvas.grid(row = 0, column = 0, sticky =(N, S, W, E))
        xscrollbar=Scrollbar(self, orient=HORIZONTAL, width = 15)
        xscrollbar.grid(row = 1, column = 0, sticky=(W,E))
        yscrollbar=Scrollbar(self, orient=VERTICAL, width = 15)
        yscrollbar.grid(row = 0, column = 1, sticky=(N, S))
        
        self.canvas.configure(scrollregion = (0, 0, mainClass.screenWidth, mainClass.screenHeight),
                                        xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
        
        self.table = Table(self.canvas, self, tablecols)

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

    def clear_STable(self):
        self.table.clear_Table()


class Table(Frame):
    def __init__(self, master, mainClass, colList, rowList = []):
        try:
            self.debugMode = mainClass.debugMode
        except:
            self.debugMode = 1
            print("debug Exception: Table")
            
        if self.debugMode > 1: print("init Table")
        
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
        if self.debugMode > 0: print("Table: fill_Table")
        if self.debugMode > 2:
            print(data)
            print(len(data[0]))

        dataCols = len(self.colList) - 1
        dataRows = len(data[0])

        for r in range(dataRows):
            TableEntry(self, 0, r + 1, str(r +1))

        for c in range(dataCols):
            for r in range(dataRows):
                TableEntry(self, c + 1, r + 1, data[c][r])

        self.update_idletasks()

    def clear_Table(self):
        for child in self.winfo_children():
            if child.__class__.__name__ == "TableEntry":
                child.destroy()

    #def setWCstate(self, frame, widgetType, newState): # set state of class of widgets in parent frame
    #        for child in frame.winfo_children():
    #            if child.__class__.__name__ == widgetType:
    #                child.configure(state = newState)

 
    def make_header(self):
        if self.debugMode > 0: print("Table: make_header")

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
            


class TableLabel(Entry):
    def __init__(self, master, col, row, dataItem):
        #print("TableLabel")
        
        self.text = StringVar()
        self.text.set(dataItem)
        Label.__init__(self, master = master)
        self.config(textvariable = self.text, width = len(dataItem) + 2)
        self.grid(column=col, row=row, sticky = 'w')

 
class TableEntry(Entry):  ## TO DO:  make this do full rows so highlight easier to apply
    def __init__(self, master, c, r, dataItem):
        try:
            self.debugMode = master.debugMode
        except:
            self.debugMode = 1
            print("debug Exception: TableEntry")
            
        #if self.debugMode > 1: print("init TableEntry")
        #if self.debugMode > 1: print(dataItem)

        Entry.__init__(self, master=master)
        self.value = StringVar()
        self.config(textvariable=self.value, relief = 'flat',
                    disabledforeground = "Black", state="readonly",
                    width = len(dataItem))
        self.grid(column=c, row=r, padx = 0, pady = 0, sticky = 'w')

        if True:
        #try:
            self.value.set(dataItem.strip())
            if c == 2:
                d = dataItem.strip()
                if d=='Ok':
                    self.config(disabledforeground = "dark green")
                elif d=="Error":
                    self.config(disabledforeground = "red4")

            self.configure(state = "disabled")
            
        #except:
            #print("Table: TableEntry Error")

#####
#####
##
## MAIN
##

if __name__ == "__main__":
    root = Tk()

    gCodeData1 = [['a', 'A'], ['b', 'B'], ['c', 'C'], ['d', 'D']] # [0] = gCodeIN, [1 / 2] = preproc result/comment, [3] = gCodeOUT
    gCodeData2 = [['k', 'K', 'kk', 'kK', 'Kk', 'KK'], ['l', 'L', 'll', 'lL', 'Ll', 'LL'],
                  ['m', 'M', 'mm', 'mM', 'Mm', 'MM'], ['n', 'N', 'nn', 'nN', 'Nn', 'NN']] # [0] = gCodeIN, [1 / 2] = preproc result/comment, [3] = gCodeOUT

    app = ScrollTableApp(root, gCodeData1, gCodeData2)

    root.mainloop()

