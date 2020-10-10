from tkinter import Tk, Button, Label
from tkinter.filedialog import askopenfilename
from os import path, listdir
from PIL.ImageTk import PhotoImage, Image
from imghdr import what
import sys

__author__ = "PRMPSmart"

PY_VERSION = int(sys.version[0])

class Block(Label):
    "A block in the grids"
    def __init__(self, master, imgfile='', h=0, w=0):
        if PY_VERSION == 3: super().__init__(master=master, relief='solid')
        else: Label(self).__init__(master=master, relief='solid')
        self.count = 0
        self.h, self.w = h, w
        self.setImage(imgfile)
    
    def setImage(self, imgfile):
        self.image = Image.open(imgfile)
        if self.h and self.w: self.image = self.image.resize((380, 170))
        self.photo = PhotoImage(self.image)
        self.config(image=self.photo)

class Grids(Tk):
    
    def __init__(self, file):
        if PY_VERSION == 3: super().__init__()
        else: Tk().__init__()

        self.title('PRMPSmart Image')
        self.count = 0
        if path.isfile(file): self.oneGrid(file)
        elif path.isdir(file): self.grids(file)
        self.attributes('-toolwindow', 1, '-topmost', 1)
        self.wm_overrideredirect(True)
        
        self.geometry('500x500+150+150')
        
        self.bind_it()
        self.mainloop()
    
    def bind_it(self):
        self._grab_anywhere_on()
        # self._grab_anywhere_off()
        self.bind('<Control-u>', exit)
        pass

    def _StartMove(self, event):
        try: self.x, self.y = event.x, event.y
        except: pass
        # self.geometry('+%d+%d'%(self.x, self.y))

    def _StopMove(self, event):
        try: self.x, self.y = event.x, event.y
        except: pass
    
    def _grab_anywhere_on(self):
        self.bind("<ButtonPress-1>", self._StartMove)
        self.bind("<ButtonRelease-1>", self._StopMove)
        self.bind("<B1-Motion>", self._OnMotion)

    def _grab_anywhere_off(self):
        self.unbind("<ButtonPress-1>")
        self.unbind("<ButtonRelease-1>")
        self.unbind("<B1-Motion>")
    
    def _OnMotion(self, event):
        try:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry("+%s+%s" % (x, y))
        except Exception as e:
            print('on motion error', e)

    def oneGrid(self, file):
        "To show only a picture"
        self.block = Block(self, file)
        self.block.place(relx=0, rely=0, relh=1, relw=1)
        
        self.geometry('%dx%d'%(self.block.image.width, self.block.image.height))
        self.bind('<Control-o>', self.loadPic)
        
    def loadPic(self, e=None):
        file = askopenfilename(filetypes=['Pictures {.jpg .png}'])
        self.oneGrid(file)

    def grids(self, file):
        "To show many pictures in a grid"
        try:
            pics = []
            for a in listdir(file):
                if path.isfile(a):
                    print(a)
                    if what(a): pics.append(path.join(file, a))
        except Exception as e: print(e)
    
        pixs = len(pics)
        print(pixs)
        if pixs:
            relh = 1 / (int(((pixs / 4) + 1 if pixs % 4 != 0 else 0)))
            k = 0
            relw = .25
            relx = 0
            rely = 0
            for pic in pics:
                co = self.count % 4
                bl = Block(self, pic, h=relh, w=relw)
                relx = co * relw
                if co == 0 and self.count != 0:
                    relx = 0
                    k += 1
                rely = k * relh
                bl.place(relx=relx, rely=rely, relh=relh, relw=relw)
                self.count += 1
            self.geometry('%dx%d'%(1400, 700))
            self.mainloop()


file_or_folder = r'C:\Users\Administrator\Documents\My\Archives\Corel Draw X7 [32-64]\images.jpg'

Grids(file_or_folder)


