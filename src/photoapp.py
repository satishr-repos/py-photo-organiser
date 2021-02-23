import os
import tkinter.font as tkFont
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import orgphoto

def select_dir(t):
    p = filedialog.askdirectory()
    if t == 'src':
        srcpath.set(p)
    else:
        destpath.set(p)
    return

def status_callback():
    pass

def organise_photos():
    print(f"source: {srcpath.get()} destination:{destpath.get()}")
    statusLbl.configure(fg="tomato")
    if os.path.isdir(srcpath.get()) == False:
        statusVar.set("Source path is not valid")
    elif os.path.isdir(destpath.get()) == False:
        statusVar.set("Destination path is not valid")
    elif destpath.get() == srcpath.get():
        statusVar.set("Source and destination path cannot be the same")
    orgphoto.do_organise(srcpath.get(), destpath.get(), status_callback)

def main():
    root = Tk()
    root.title("Organise Photos App")
    #root.geometry("550x600")
    
    frame1 = ttk.LabelFrame(root, text="", height=50)
    frame1.pack(expand="yes", fill="both", padx=10, ipady=10, ipadx=10)

    # get source path for photos
    global srcpath
    srcpath = StringVar()

    srcLbl = Label(frame1, text="Source Path: ", pady=5, padx=10)
    srcLbl.grid(sticky=W, row=0, column=0)
    
    srcEntry = ttk.Entry(frame1, textvariable=srcpath, width=60)
    srcEntry.grid(row=1, column=0, padx=(10,0))

    srcBtn = Button(frame1, text="Browse...", padx=10, command=lambda : select_dir('src'))
    #queryBtn.config(width=20)
    srcBtn.grid(row=1, column=4, padx=5)

    # get destination path for photos
    global destpath
    destpath = StringVar()

    destLbl = Label(frame1, text="Destination Path: ", pady=5,padx=10)
    destLbl.grid(sticky=W, row=2, column=0)
    
    destEntry = ttk.Entry(frame1, textvariable=destpath, width=60)
    destEntry.grid(row=3, column=0, padx=(10,0))

    destBtn = Button(frame1, text="Browse...", padx=10, command=lambda : select_dir('dest'))
    #queryBtn.config(width=20)
    destBtn.grid(row=3, column=4, padx=5)

    # add button to handle the task
    orgBtn = Button(frame1, text="Organise Photos", padx=10, command=organise_photos)
    #queryBtn.config(width=20)
    orgBtn.grid(sticky=W, row=4, column=0, padx=10, pady=10)

    # add status bar
    global statusVar
    statusVar = StringVar()
    fontStyle = tkFont.Font(family="Helvetica", size=12)
    global statusLbl
    statusLbl = Label(root, textvariable=statusVar, bd=1, relief=SUNKEN, font=fontStyle, anchor=W)
    statusLbl.pack(expand="yes", fill="both", padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
