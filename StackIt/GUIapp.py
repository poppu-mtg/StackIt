import os, sys, time
from StackIt import globals, builder

if sys.version_info.major == 3:
    from tkinter import *
else:
    from Tkinter import *
# from tkFileDialog import *

from PIL import Image, ImageTk


class ScrollIt():

    def __init__(self):
        self.image1 = Image.open(mGui.btn2text.get()[9:] + '-scroll.png')
        w1, h1 = self.image1.size
        self.imagefull = Image.new("RGB", (w1 * 2, h1), "black")
        self.imagefull.paste(self.image1, (0, 0))
        self.imagefull.paste(self.image1, (w1, 0))

        self.photo1 = ImageTk.PhotoImage(self.imagefull)
        width1 = self.photo1.width()
        height1 = self.photo1.height()

        novi1 = Toplevel()
        self.canvas1 = Canvas(novi1, width=1980, height=34)
        self.canvas1.pack(expand=1, fill=BOTH) # <--- Make your canvas expandable.
        x = (width1)/2.0
        y = (height1)/2.0
        self.item = self.canvas1.create_image(x, y, image=self.photo1) # <--- Save the return value of the create_* method.
        self.x00, self.y00 = self.canvas1.coords(self.item)
        self.canvas1.bind('<Button-1>', self.next_image)

    def next_image(self, even=None):

        x0, y0 = self.canvas1.coords(self.item)
        if x0 < 3:
            self.canvas1.coords(self.item, (self.x00, y0))
        else:
            self.canvas1.move(self.item, -3, 0)

        self.canvas1.after(60, self.next_image)


def OpenPro1():
    if mGui.Listname.get() != '':
        deckname = mGui.Listname.get()
    elif len(mGui.Listentry.get("1.0", "end-1c")) != 0:
        deckname = 'sample.txt'
        if os.path.isfile(deckname):
            os.remove(deckname)
        decktext = mGui.Listentry.get("1.0", 'end-1c')
        with open(deckname, "a") as outf:
            outf.write(decktext + '\n')

    builder.main(deckname)

    if deckname == 'sample.txt':
        if os.path.exists(os.path.join(globals.CACHE_PATH, deckname)):
            os.remove(os.path.join(globals.CACHE_PATH, deckname))

        os.rename(deckname, os.path.join(globals.CACHE_PATH, deckname))

    novi = Toplevel()
    canvas = Canvas(novi, width = 350, height = 1000)
    canvas.pack(expand = YES, fill = BOTH)
    #gif1 = PhotoImage(file = 'image.gif')
    gif1=ImageTk.PhotoImage(Image.open(deckname[:-4] + '.png'))
    canvas.create_image(50, 10, image = gif1, anchor = NW)
    #assigned the gif1 to the canvas object
    canvas.gif1 = gif1

    mGui.btn2text.set('BannerIt ' + deckname[:-4])
    mGui.Button_2.config(state='active')

def OpenPro2():
    ScrollIt()


mGui = Tk()
mGui.configure(background='white')

mGui.title('  StackIt')
mGui.geometry("350x565")

tkimage = ImageTk.PhotoImage(Image.open(os.path.join(globals.RESOURCES_PATH, 'StackIt-Logo.png')).resize((345, 87)))
mGui.Logo = Label(mGui, image=tkimage)
mGui.Logo.grid(row=0, column=0, columnspan=3)

mGui.Label1 = Label(mGui, text=' Decklist:')
mGui.Label1.grid(row=1, column=0)

mGui.Listname = Entry(mGui)
mGui.Listname.grid(row=1, column=1)

mGui.Button_1 = Button(mGui, text="Generate", command=OpenPro1)
mGui.Button_1.grid(row=1, column=2)

#mGui.Listentry=Entry(mGui)
#mGui.Listentry.grid(row=2, column=0, columnspan=3)

mGui.Label2 = Label(mGui, text=' Paste board:')
mGui.Label2.grid(row=2, column=0, columnspan=3)

mGui.Listentry=Text(mGui, height=25, width=40, relief=GROOVE, undo=True, xscrollcommand=True, yscrollcommand=True, bd=2)
mGui.Listentry.grid(row=3, column=0, columnspan=3)

mGui.btn2text = StringVar()
mGui.btn2text.set('BannerIt     ')
mGui.Button_2 = Button(mGui, textvariable=mGui.btn2text, state='disabled', command=OpenPro2)
mGui.Button_2.grid(row=4, column=0, columnspan=3)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--automatedtest":
        def draw():
            mGui.update_idletasks()
            mGui.update()

        draw()
        mGui.Listentry.insert(END, "60 Island\n4 Urza's Tower\n200 Shadowborn Apostle")
        draw()
        OpenPro1()
        draw()
        mGui.Listname.insert(END, "testdecks/StressTest1.dec")
        draw()
        OpenPro1()
        draw()
        time.sleep(1)
    else:
        mGui.mainloop()

if __name__ == "__main__":
    main()
