from tkinter import * 

root = Tk()

def myClick():
    # Upon click the text will trigger
    # This is used as a input function
    label = Label(root, text='button')
    label.pack()

button = Button(root, text='click', padx=10,pady=10, command=myClick)
button.pack()

# THis needs to loop so it keeps running 
root.mainloop()



