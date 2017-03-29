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



#class MainWindow():
#
#    #----------------
#
#    def __init__(self, main):
#
#        main.title('  StackIt')
#        main.geometry("370x300")
#    
#        # canvas for image
#        self.canvas = Canvas(main, width=350, height=1000)
#        mywidth=370
#        self.canvas.grid(row=0, column=0)
#        image=Image.open('/Users/grd/Perso/MTG/TestGit/StressTest1.png')
#        photo=ImageTk.PhotoImage(image)
#        self.image_on_canvas = self.canvas.create_image(0, 0, anchor = NW, image = photo)
#
#        self.GuiLabel1 = Label(main,text=' Decklist:')
#        self.GuiLabel1.grid(row=1, column=0)
#
#        self.GuiListname=Entry(main)
#        self.GuiListname.grid(row=1, column=1)
#
#        self.GuiButton_1 = Button(main,text="Generate",command=lambda:self.OpenPro1(main))
#        self.GuiButton_1.grid(row=1, column=2)
#
#        # images
#        #self.my_images = []
#        #self.my_images.append(PhotoImage(file = "ball1.gif"))
#        #self.my_images.append(PhotoImage(file = "ball2.gif"))
#        #self.my_images.append(PhotoImage(file = "ball3.gif"))
#        #self.my_image_number = 0
#        self.isImage = 0
#
#        # set first image on canvas
##        self.image_on_canvas = self.canvas.create_image(0, 0, anchor = NW, image = self.my_images[self.my_image_number])
#
#        # button to change image
##        self.button = Button(main, text="Change", command=self.onButton)
##        self.button.grid(row=1, column=0)
#
#    #----------------
#
#    def OpenPro1(self,main):
#
#        sys.argv = ['StackIt.py','StressTest1.dec']
#        execfile('StackIt.py',globals())
#
#        # load image
#        #self.canvas.itemconfig(self.image_on_canvas, image = self.my_images[self.my_image_number])
#        image=Image.open('/Users/grd/Perso/MTG/TestGit/StressTest1.png')
#        photo=ImageTk.PhotoImage(image)
#
#        mywidth, myheight = image.size
#        print(mywidth,myheight)
#        
#        #first time generating
#        if self.isImage == 0:
#            self.image_on_canvas = self.canvas.create_image(0, 0, anchor = NW, image = photo)
#            #self.canvas.itemconfig(self.image_on_canvas, image = photoself.my_images[self.my_image_number])
#            self.isImage = 1
#        
#        
#
##----------------------------------------------------------------------
#
#root = Tk()
#MainWindow(root)
#root.mainloop()
#
