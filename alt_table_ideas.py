#!/usr/bin/python2.7

from Tkinter import *

class table_alt1(Frame, object):
    def __init__(self, master):
        super(table_alt1, self).__init__(master)

        self.scrollbar = Scrollbar(self)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox = Listbox(self)
        self.listbox.pack()
        for i in range(20):
            self.listbox.insert(END, i)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.update_idletasks()


#####
# MAIN

root = Tk()

table = table_alt1(root)
table.master.title("Table1")

root.mainloop()


#####
# ORIG

##root = Tk()
##
##scrollbar = Scrollbar()
##scrollbar.pack(side=RIGHT, fill=Y)
##listbox = Listbox()
##listbox.pack()
##for i in range(20):
##    listbox.insert(END, i)
##listbox.config(yscrollcommand=scrollbar.set)
##scrollbar.config(command=listbox.yview)
##
##mainloop()
