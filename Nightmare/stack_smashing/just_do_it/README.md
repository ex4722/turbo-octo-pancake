This challenge was a hard challenge for me because I had no idea what I should have been doing, so let's get right into this challenge
Opening the challenge in ghidra we see that the main function seems pretty safe and normal

![image](https://user-images.githubusercontent.com/77011982/123354657-127a0600-d532-11eb-97e4-0ca64fde1bf5.png)

The Program simply checks your password against a already set password and if it's correct it prints success but no flag, so how the heck we supposed to get the flag? I was stuck on this question for a looooong time but the answer was actually very simple. 
First things first let's just try to get a success message. This confused me for a while because when you enter the password found in the binary you get an extra newline character as shown below in gdb. 

![image](https://user-images.githubusercontent.com/77011982/123354982-b5cb1b00-d532-11eb-8f62-5cbea9846856.png)

This stumped me for a while until I remembered the idea of a null byte terminator that works in C. This is the byte \x00 which is used to end a string. We could do something like P@SSW0RD and then append to it a null byte and then the newline character to send it but the enter is not read. Using python we can try this and turns out it works. 

![image](https://user-images.githubusercontent.com/77011982/123355092-f0cd4e80-d532-11eb-947b-62872634a07f.png)

Great, we got the password but wheres the flag. The answer lies in how the stack is laid out. In ghidra we see how the stack is laid out with the user input above the flag that sets the output message.

![image](https://user-images.githubusercontent.com/77011982/123355337-78b35880-d533-11eb-84c0-076ac454228f.png)

This may sound very confusing as the image shows that the user_input is below it in the image but this actually makes sense. The stack grows from higher address to lower address and base point is used to get the offsets to load the variables. Here a visual to make this a little more clear 

![image](https://user-images.githubusercontent.com/77011982/123355819-700f5200-d534-11eb-9f2e-5a80018fb837.png)

 After the fgets to get the user input it then goes to validate the user input and changes the value as the out_put if it's not the same. The interesting part is that the failure message is set beforehand and thus if we overwrite it we can change the failure message. This means that we just need to fail on purpose but overwrite the pointer that the out_put variable is pointing to the value of the flag. 
 
 Now the challenge is much easier because it only takes 14 bytes to bytes to overwrite this and we can write 20 bytes according to the fgets parameters. So the plan is the write 14 bytes of data to get up to the point before the out_put message location and then write the value of where the flag is stored. 
 
 This was the hardest part of the challenge for me as I didn't know how to find the flag in memory. I tried to run the process and break near the end and then used gdb to find the string but somehow it didn't work. After a lot of StackOverflow and thinking I finally figured out how to find it. If we look in the code there is a section that checks if the current flag is not set to anything. Then I set a breakpoint at that address to see the parameters that were on the stack and I found it as it is pushed on the stack to run strcmp on it 
 
 ![image](https://user-images.githubusercontent.com/77011982/123442946-6b35b700-d5a3-11eb-8fb9-e9f06076868d.png)

This means that the address that points to the flag is stored at `0x804a080`. This means we need to overwrite the parameter that is passed to the puts. 
 
 
 
![image](https://user-images.githubusercontent.com/77011982/123356806-61299f00-d536-11eb-9bf6-2263b6f5ad71.png)

This means that now we just need to test for the offset to overwrite at and then write the correct address keeping in mind endianess and we get the flag. 

![image](https://user-images.githubusercontent.com/77011982/123443226-b94aba80-d5a3-11eb-9a6f-3b09f6ab1671.png)


`TWCTF{pwnable_warmup_I_did_it!}`

Whef that was a really hard warmup challenge :) 
