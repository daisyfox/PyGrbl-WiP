
#!/usr/bin/python2.7

"""
PyGrbl_GUI Class & PyGrbl_Wii Class

"""

from Tkinter import *
from ScrolledText import * # for Editor
from tkMessageBox import *
import os, time, tkFont
import webbrowser, os.path
from tkFileDialog import askopenfilename, asksaveasfile

from PyGrbl_gCodeChecker import *
from PyGrbl_Visualiser import *
from PyGrbl_Control import *

class PyGrbl_GUI(Frame, object):
    def __init__(self, master):
        super(PyGrbl_GUI, self).__init__(master)

        self.master = master # master = 'root'

        ##  WHO AM I ?
        #print("Who am I: " + self.winfo_class())  # = 'Frame' !!
        #print("Who am I: " + self.__class__.__name__) # = 'PyGrbl_GUI'

        self.master.protocol("WM_DELETE_WINDOW", self.onExit)

        #--------------------------------------------------------------------
        # APPLICATION WIDE VARIABLES
        #--------------------------------------------------------------------

        self.debugMode = 1 # 0=None, 1=Exit procedures OK/Error, 2 = Everything

        #  apps running
        self.apps = [] # list of apps for goto menu & knowing what  is running
        self.apps.append(self.__class__.__name__)
        self.currentApp = ""

        #self.helpBrowser = webbrowser.get('epiphany')
        #self.helpBrowser = webbrowser.get('netsurf')
        self.helpBrowser = webbrowser
        #self.url = '/home/pi/PyGrbl_Dev/GrblUserGuide/Grbl0.9gUserGuide.html'
        self.url = '/home/pi/PyGrbl_Dev/PyGrblHelp.html'

        self.fileOpenFlag = BooleanVar()
        self.fileOpenFlag.set(False)
        self.gCodeErrFlag = BooleanVar()
        self.gCodeErrFlag.set(False)

        # shared variables / data
        self.gCodeFilename = ""
        self.gCodeData = [[], [], [], []]

        #--------------------------------------------------------------------
        # GUI SETUP
        #--------------------------------------------------------------------

        SW = self.master.winfo_screenwidth()
        SH = self.master.winfo_screenheight()

        self.screenWidth = int(SW * 0.90)
        self.screenHeight = int(SH * 0.80)
        self.widgetscale = SW / 800 # ????
        self.fontscale = SW / 80

        for fontname in ["TkDefaultFont", "TkTextFont", "TkMenuFont",
                         "TkCaptionFont", ]:
            default_font = tkFont.nametofont(fontname)
            default_font.configure(size = self.fontscale)

        self.bind("<Configure>", self.onResize)

        self.master.geometry(str(self.screenWidth) + "x" + str(self.screenHeight - 30))
        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)
        self.grid(column = 0, row = 0, sticky = (N, S, W, E))

        self.createMenu()
        self.mainFrame = Frame(self)
        self.mainFrame.grid(row = 0, column = 0, sticky = (N, S, W, E))
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)

        self.createStatusbar(self, 1, 0)
        self.update_idletasks()

    #--------------------------------------------------------------------
    # CREATE GUI MAIN WINDOW, MENU & STATUS BAR
    #--------------------------------------------------------------------
    def createMenu(self):
        try:
            self.menubar = Menu(self.master)
            self.master.configure(menu = self.menubar)

            self.filemenu = Menu(self.menubar, tearoff = False)
            self.filemenu.add_command(label = "Open", command = lambda: self.openFile())
            self.filemenu.add_command(label = "Close", state = "disabled", command = lambda: self.closeFile())
            self.menubar.add_cascade(label = "gCode File", menu = self.filemenu)

            self.servicemenu = Menu(self.menubar, tearoff = False)
            self.servicemenu.add_command(label = "Control Panel", state = "disabled",
                                         command = lambda: self.menuOptionSelected(self.ControlPanel))
            self.servicemenu.add_command(label = "gCode Checker", state = "disabled",
                                         command = lambda: self.menuOptionSelected(self.gCodeChecker))
            self.servicemenu.add_command(label = "Visualiser", state = "disabled",
                                         command = lambda: self.menuOptionSelected(self.Visualiser))
            self.servicemenu.add_command(label = "Editor", state = "disabled",
                                         command = lambda: self.menuOptionSelected(self.Editor))
            self.menubar.add_cascade(label = "Service", menu = self.servicemenu)

            self.menubar.add_command(label = "Help", command = lambda: self.helpBrowser.open(self.url)
)
            self.menubar.add_command(label = "Exit", command = lambda: self.onExit())

            if self.debugMode > 0:
                print("CreateMenu: Ok")

        except:
            if self.debugMode > 0:
                print("CreateMenu: Error")

    def createStatusbar(self, outerFrame, r, c):
        try:
            self.statusbar = Frame(outerFrame)
            self.statusbar.grid(row = r, column = c, sticky = W+E)

            self.statusbarList = ["System Status: Ok", "", ""]
            self.statusbarText = StringVar()
            self.statusbarText.set(self.statusbarList[0])
            self.statusbarLabel = Label(self.statusbar, textvariable = self.statusbarText,
                                                anchor = W, bg = "White")
            self.statusbarLabel.pack(fill = BOTH)

            if self.debugMode > 0:
                print("CreateStatusbar: Ok")

        except:
            if self.debugMode > 0:
                print("CreateStatusbar: Error")


    #--------------------------------------------------------------------
    # NAVIGATION
    #--------------------------------------------------------------------
    def todo(self):
        #default command during development
        pass

    def onResize(self, event):
        SW = self.winfo_width()
        self.fontscale = int(SW / 80)
        if self.fontscale < 8: self.fontscale = 8

        for fontname in ["TkDefaultFont", "TkTextFont", "TkMenuFont",
                         "TkCaptionFont", "TkFixedFont" ]:
            default_font = tkFont.nametofont(fontname)
            default_font.configure(size = self.fontscale)
        
        if 'PyGrbl_ControlPanel' in self.apps:
            self.ControlPanel.JogButtonFont.configure(size = int(self.fontscale * 2.5))

        self.update_idletasks()
   

    def onExit(self):
        try:
            if askokcancel("Just Checking", "Do you want to close now?"):
                #if self.wii.wiiState == "Connected": self.wii.wiiStop()
                if self.fileOpenFlag.get() == True: self.closeFile()
                self.master.destroy()

            if self.debugMode > 0: print("on Exit: Ok")

        except:
            if self.debugMode > 0:
                print("on Exit: Error")

    def menuOptionSelected(self, selection):
        try:
            if selection != self.currentApp:
                #self.currentApp.grid_forget() # configure settings lost
                self.currentApp.grid_remove() # configure settings retained
                self.currentApp = selection
                self.currentApp.grid()
                self.update_idletasks()

            if self.debugMode > 0:
                print("Menu Option Selected: Ok")

        except:
            if self.debugMode > 0:
                print("Menu Option Selected: Error")

    #-------------------------------------------------
    # gCODE FILE MENU
    #-------------------------------------------------
    def openFile(self):
        if self.fileOpenFlag.get() == True:
            self.closeFile()

        try:
            self.gCodeFilename = askopenfilename()

            if self.gCodeFilename:
                self.fileShortname =os.path.split(self.gCodeFilename)[1]
                self.inFile = open(self.gCodeFilename, 'r')

                self.fileOpenFlag.set(True)
                self.filemenu.entryconfig("Close", state = "normal")

                if self.debugMode > 1: print("Open File (Y): Ok")

            else:
                if self.debugMode > 1: print("Open File (N): Ok")

        except:
            if self.debugMode > 0: print("Open File: Error")

    def closeFile(self):
        try:
            if askyesno("Close File", "This option does NOT save the gCode file.  \n\nContinue with close ?"):
                self.inFile.close()
                self.fileOpenFlag.set(False)
                self.filemenu.entryconfig("Close", state = "disabled")

                if self.debugMode > 1: print("Close File (Y): Ok")

            else:
                if self.debugMode > 1: print("Close File (N): Ok")

        except:
            if self.debugMode > 0: print("Close File: Error")


#-------------------------------------------------
# PyGrbl_Editor
#-------------------------------------------------
class PyGrbl_Editor(Frame):
    def __init__(self, master, app):
        Frame.__init__(self, master = master)

        ##  WHO AM I ?
        #print("Who am I:  " + self.winfo_class())  # = 'Frame' !!
        #print("Who is my master: " + master.__class__.__name__) # = Frame
        #print("Who is my app: " + app.__class__.__name__) # = PyGrbl_GUI
        #print("Who am I:  " + self.__class__.__name__) # = 'PyGrbl_Editor'

        self.app = app
        self.app.servicemenu.entryconfig("Editor", state = "normal")
        self.app.apps.append(self.__class__.__name__)
        self.openFileTrace = self.app.fileOpenFlag.trace_variable('w', self.fileOpenTraceAction)

        self.editorWaiting = False # to prevent conflict gCodeChecker & Editor 'fileOpenTrace'

        self.createEditorWidgets()
        
        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)
        self.grid(column = 0, row = 0, sticky = (N, S, W, E))


    def createEditorWidgets(self):
        # Text Pad
        self.textPad = ScrolledText(self, width = 30, height = 10, font = "TkTextFont")
        self.textPad.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = (N, S, W, E))
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)

        self.save = Button(self, text = "Save", width = 6, command = lambda: self.saveFile())
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


#-------------------------------------------------
# MAIN
#-------------------------------------------------

if __name__ == "__main__":

    root = Tk()
    app = PyGrbl_GUI(root)
    app.master.title("PyGrbl v 0.2 (dev)")

    app.wiiMoteYes = False

    if app.wiiMoteYes:
        import cwiid
        app.wiiMote = PyGrbl_Wii(app.mainFrame, app)

    app.ControlPanel = PyGrbl_ControlPanel(app.mainFrame, app)
    app.ControlPanel.grid_remove() # grid_forget loses configure settings
    app.gCodeChecker = PyGrbl_gCodeChecker(app.mainFrame, app)
    app.gCodeChecker.grid_remove()
    app.Visualiser = PyGrbl_Visualiser(app.mainFrame, app)
    app.Visualiser.grid_remove()

    app.Editor = PyGrbl_Editor(app.mainFrame, app)

    app.currentApp = app.Editor # the 'not forgotten/removed' app

    root.mainloop()
