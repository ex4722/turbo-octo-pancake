from tkinter import * 

current_equation = ''
root = Tk()
def myClick(name):
    # SOmehow this solved the declared before issues 
    global current_equation
    global bar
    # This gives the text portion of the current function so we get the character
    character = name.config('text')[-1]
    print(character)
    # Message just shows the user the numbers they inputed 
    message = Label(root,text=character)
    message.grid(row=5,column=2)
    message.pack
    bar.destroy()
    # If = sign then eval the question and clear current buffer 
    if character == '=':
        print(eval(current_equation))
        bar = Label(root,text=eval(current_equation), height = 3)
        if eval(current_equation) == 1337:
            for widget in root.winfo_children():
                widget.forget()
            new = Tk()
            foo = Label(new, text = "VIM MASTERRACE",width = 100, font=('Arial', 100), fg='blue', bg = 'red').pack()




        bar.grid(row=0, column=0)
        current_equation = ''
    else:
        # If not equal sign just add onto the equation and display it
        current_equation += character
        bar = Label(root,text=current_equation, height = 3)
        bar.grid(row=0, column=0)
    return None



# Declare all the buttons with text names and a lambda function to return its name into the function
bar = Label(root,text='Easter Egg',height=3)
button1 = Button(root, text='1', padx=50,pady=50, command=lambda: myClick(button1))
button2 = Button(root, text='2', padx=50,pady=50, command=lambda: myClick(button2))
button3 = Button(root, text='3', padx=50,pady=50, command=lambda: myClick(button3))
button4 = Button(root, text='4', padx=50,pady=50, command=lambda: myClick(button4))
button5 = Button(root, text='5', padx=50,pady=50, command=lambda: myClick(button5))
button6 = Button(root, text='6', padx=50,pady=50, command=lambda: myClick(button6))
button7 = Button(root, text='7', padx=50,pady=50, command=lambda: myClick(button7))
button8 = Button(root, text='8', padx=50,pady=50, command=lambda: myClick(button8))
button9 = Button(root, text='9', padx=50,pady=50, command=lambda: myClick(button9))
button0 = Button(root, text='0', padx=50,pady=50, command=lambda: myClick(button0))
Plus = Button(root, text='+', padx=50,pady=50, command=lambda: myClick(Plus))
equal = Button(root, text='=', padx=50,pady=50, command=lambda: myClick(equal))
sub = Button(root, text='-', padx=50,pady=50, command=lambda: myClick(sub))
mul = Button(root, text='*', padx=50,pady=50, command=lambda: myClick(mul))
divide = Button(root, text='/', padx=50,pady=50, command=lambda: myClick(divide))
period = Button(root, text='.', padx=50,pady=50, command=lambda: myClick(period))
exit_but = Button(root, text='Exit', command=root.quit)


# Using grid to place the keys in a nice order 
button1.grid(row=3, column = 0)
button2.grid(row=3, column = 1)
button3.grid(row=3, column = 2)
sub.grid(row =3 , column =3)

button4.grid(row=2, column = 0)
button5.grid(row=2, column = 1)
button6.grid(row=2, column = 2)
mul.grid(row=2, column = 3)

button7.grid(row=1, column = 0)
button8.grid(row=1, column = 1)
button9.grid(row=1, column = 2)
divide.grid(row=1,column =3)


button0.grid(row=4, column = 0)
period.grid(row=4,column=1)
Plus.grid(row=4, column = 2)
equal.grid(row=4, column = 3)
bar.grid(row=0, column=0)
exit_but.grid(row=5,column=0)



# sticking it onto the root
exit_but.pack
button1.pack
button2.pack
button3.pack
button4.pack
button5.pack
button6.pack
button7.pack
button8.pack
button9.pack
button0.pack





# THis needs to loop so it keeps running 
root.mainloop()



