#!/usr/bin/python2.7

"""
gCode Editor

"""

from Tkinter import *
from ScrolledText import *
from tkFileDialog import asksaveasfile

from PyGrbl_GUI import *

class PyGrbl_Editor(Frame):    
    def __init__(self, master, app):
        Frame.__init__(self, master = master)

        ##  WHO AM I ?
        #print("Who am I:  " + self.winfo_class())  # = 'Frame' !!
        #print("Who is my parent: " + app.__class__.__name__) # = PyGrbl_GUI
        #print("Who am I:  " + self.__class__.__name__) # = 'PyGrbl_Editor'
        
        self.app = app
        self.app.servicemenu.entryconfig("Editor", state = "normal")
        self.app.apps.append(self.__class__.__name__)
        self.openFileTrace = self.app.fileOpenFlag.trace_variable('w', self.fileOpenTraceAction)

        self.screenWidth = self.app.screenWidth - 20
        self.screenHeight = self.app.screenHeight - 50
        self.editorWaiting = False

        self.createEditorWidgets()
        self.grid()


    def createEditorWidgets(self):
        # Text Pad
        self.textPad = ScrolledText(self, width = 70, height = 20, font = (14))
        self.textPad.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = (N, S, W, E))
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        
        self.save = Button(self, text = "Save", command = lambda: self.saveFile())
        self.save.grid(row = 0, column = 1, padx = 10, pady = 10, sticky = N)
        

    def fileOpenTraceAction(self, name, index, mode):
        try:
            if self.app.fileOpenFlag.get() == True:
                if self.app.currentApp == self.app.Editor:
                    contents = self.app.inFile.read()
                    contents = contents.replace('\r', '')
                    self.app.inFile.seek(0) # reset inFile cursor to top of file
                    self.textPad.insert(1.0, contents)
                elif self.editorWaiting:
                    contents = self.app.inFile.read()
                    self.app.inFile.seek(0) # reset inFile cursor to top of file
                    self.textPad.insert(1.0, contents)
                    self.editorWaiting = False
                else:
                    self.editorWaiting = True
                    self.after(1000, self.fileOpenTraceAction(name, index, mode))

            elif self.app.fileOpenFlag.get() == False:
                self.textPad.delete(1.0, END)

            if self.app.debugMode > 1: print("fileOpenTraceAction: Ok")

        except:
            print("fileOpenTraceAction: Error")


    def saveFile(self):
        filename = asksaveasfile(mode = 'w')
        if filename:
            data = self.textPad.get(1.0, END+'-1c')
            filename.write(data)
            filename.close()

#####
#####
##
## MAIN
##

if __name__ == "__main__":
    root = Tk()

    app = PyGrbl_GUI(root)
    app.master.title("PyGrbl Editor")

    app.Editor = PyGrbl_Editor(app.mainFrame, app)
    app.currentApp = app.Editor
    
    root.mainloop()
