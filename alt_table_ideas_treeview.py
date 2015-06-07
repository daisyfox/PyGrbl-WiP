#!/usr/bin/python2.7

from Tkinter import *
import ttk


#####
# ORIG

root = Tk()

#Frame
frame = ttk.Frame(root)
frame.master.title("Table using ttk Treeview")
frame.pack(side=TOP, fill=BOTH, expand=Y)

#Tree
tree = ttk.Treeview()
tree["columns"] = ("col1", "col2", "col3", "col4")
tree.column('#0', width = 0) # to hide the default first column
tree.column("col1", width = 100)
tree.column("col2", width = 100)
tree.column("col3", width = 100)
tree.column("col4", width = 100)
tree.heading("col1", text = "Column 1")
tree.heading("col2", text = "Column 2")
tree.heading("col3", text = "Column 3")
tree.heading("col4", text = "Column 4")

for c in range(200):
    tree.insert("", 'end', values = ("Line " + str(c), "abc", "ABC", "123"))

#ScrollBars
yScBar = ttk.Scrollbar(orient=VERTICAL, command = tree.yview)
tree['yscroll'] = yScBar.set
xScBar = ttk.Scrollbar(orient=HORIZONTAL, command = tree.xview)
tree['xscroll'] = xScBar.set


#Add Tree & Scrollbars to Frame
tree.grid(in_ = frame, row = 0, column = 0, sticky = (N, S, W, E))
yScBar.grid(in_ = frame, row = 0, column = 1, sticky = (N, S))
xScBar.grid(in_ = frame, row = 1, column = 0, sticky = (W, E))

#Resizing config
frame.rowconfigure(0, weight = 1)


root.mainloop()
