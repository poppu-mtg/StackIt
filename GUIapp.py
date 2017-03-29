import os, sys, time
import globals

if sys.version_info.major == 3:
    from tkinter import *
else:
    from Tkinter import *
# from tkFileDialog import *

from PIL import Image, ImageTk


def OpenPro1():
    if mGui.Listname.get() != '':
        deckname = mGui.Listname.get()
    elif len(mGui.Listentry.get("1.0", "end-1c")) != 0:
        deckname = 'sample.txt'
        decktext = mGui.Listentry.get("1.0",'end-1c')
        with open(deckname, "a") as outf:
            outf.write(decktext + '\n')

    import StackIt
    StackIt.main(deckname)

    if deckname == 'sample.txt':
        if os.path.exists(os.path.join(globals.CACHE_PATH, deckname)):
            os.remove(os.path.join(globals.CACHE_PATH, deckname))

        os.rename(deckname, os.path.join(globals.CACHE_PATH, deckname))

    novi = Toplevel()
    canvas = Canvas(novi, width = 350, height = 1000)
    canvas.pack(expand = YES, fill = BOTH)
    #gif1 = PhotoImage(file = 'image.gif')
    gif1=ImageTk.PhotoImage(Image.open(deckname[:-4]+'.png'))
    canvas.create_image(50, 10, image = gif1, anchor = NW)
    #assigned the gif1 to the canvas object
    canvas.gif1 = gif1


mGui = Tk()
mGui.configure(background='white')

mGui.title('  StackIt')
mGui.geometry("350x550")

tkimage = ImageTk.PhotoImage(Image.open(os.path.join(globals.RESOURCES_PATH, 'StackIt-Logo.png')).resize((345,87)))
mGui.Logo = Label(mGui, image=tkimage)
mGui.Logo.grid(row=0, column=0, columnspan=3)

mGui.Label1 = Label(mGui,text=' Decklist:')
mGui.Label1.grid(row=1, column=0)

mGui.Listname = Entry(mGui)
mGui.Listname.grid(row=1, column=1)

mGui.Button_1 = Button(mGui,text="Generate",command=OpenPro1)
mGui.Button_1.grid(row=1, column=2)

#mGui.Listentry=Entry(mGui)
#mGui.Listentry.grid(row=2, column=0, columnspan=3)

mGui.Label2 = Label(mGui,text=' Paste board:')
mGui.Label2.grid(row=2, column=0, columnspan=3)

mGui.Listentry=Text(mGui, height=25, width=40, relief=GROOVE, undo=True, xscrollcommand=True, yscrollcommand=True, bd=2)
mGui.Listentry.grid(row=3, column=0, columnspan=3)

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

