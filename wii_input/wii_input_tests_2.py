from Tkinter import *

class wiiHandler(Frame):
    def __init__(self, master):
        
        self.frame = Frame(root, width = 100, height = 100)
        self.frame.bind("<Key>", self.key)
        self.frame.bind("<Button-1>", self.callback)
        self.frame.pack()
    
    def key(self, event):
        #print "Key pressed:  ", event.keycode, "   Key state: ", event.state
        key_pressed = event.keycode
        key_state = event.state
        
# A         = KEY_A (38)  /  KEY_ENTER (36)
# B         = KEY_B (50 - but used as state modifier (state = 1))
# Up       = KEY_UP (111)
# Down	= KEY_DOWN (116)
# Left	= KEY_LEFT (113)
# Right	= KEY_RIGHT (114)
# Minus	= KEY_BACK (166)
# Plus	= KEY_FORWARD (167)
# Home	= KEY_HOME (110)
# 1	= KEY_1 (10)
# 2	= KEY_2 (11)

        if key_pressed == 36: print("A")
        elif key_pressed == 50: print("B")
        elif key_pressed == 113: print("LEFT")
        elif key_pressed == 114: print("RIGHT")
        elif key_pressed == 166: print("MINUS")
        elif key_pressed == 167: print("PLUS")
        elif key_pressed == 110: print("HOME")
        elif key_pressed == 10: print("1")
        elif key_pressed == 11: print("2")

        elif key_pressed == 111:
            if event.state == 0: print("UP")
            else: print("B & UP")
        elif key_pressed == 116:
            if event.state == 0: print("DOWN")
            else: print("B & DOWN")


    def callback(self, event):
        self.frame.focus_set()
        print("clicked at", event.x, event.y)


if __name__ == "__main__":
    root = Tk()

    app = wiiHandler(root)
    root.mainloop()
