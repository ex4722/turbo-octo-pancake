from tkinter import * 

root = Tk()

myLabel = Label(root, text="Hello world")
myLabel1 = Label(root, text="Name is Eddie")


# Rows show location on where it is things are relative to each other 
 myLabel.grid(row=0,column=0)
myLabel1.grid(row=1, column = 0)


# THis needs to loop so it keeps running 
root.mainloop()



