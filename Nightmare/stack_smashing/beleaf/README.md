This challenge was similar to the first challenge except for the fact that it was stripped and the flag was a little obfuscated. When we open it up in Ghidra we notice that none of the functions have names. That's a bummer as it means we need to find the main, luckily it's not too hard as the program is dynamically linked to the libc library needs to know the main function. 
Thus we can open the entry point and look for the first value passed into __libc_start_main and upon opening it we see something that looks like the main function. 
![image](https://user-images.githubusercontent.com/77011982/122582121-c73d9000-d025-11eb-9153-7e9859e4af78.png)

![image](https://user-images.githubusercontent.com/77011982/122582150-cefd3480-d025-11eb-84d6-b70bd3467ec2.png)

The second way to find the main function involves using gdb to find the same entry point. Using GDB we can first run `` info file`` to get all the locations of the types of data. The one we are interested in is the .text which is the beginning of the instructions. 
![image](https://user-images.githubusercontent.com/77011982/122582450-2f8c7180-d026-11eb-8f43-e30343734fec.png)

We can use examine the instructions at this location to find the entry point of the function. 
`` x/15i 0x00005555554006f0`` 

![image](https://user-images.githubusercontent.com/77011982/122582558-48952280-d026-11eb-8e68-58bd3c0054ac.png)

One line that stuck out like a sore thumb was the line that loads an instruction into RIP which is followed by a call function. This means that the first function called is at the location of the main function. 
If we `` x/20i 0x5555554008a1 `` we can what seems like the main function as well. 
![image](https://user-images.githubusercontent.com/77011982/122583068-da9d2b00-d026-11eb-8ad2-0b42b4eed472.png)


With the main function found we can now examine it some more we see that the length of the flag is first compared with hex 21 which is 33 in decimal, thus the flag is probably 33 characters long. Afterwards, each character of the flag is passed into a function and then the output is compared to a blob of data which differs every time as the iterator changes
When we look at the blob of data we see a number every 8 bytes. This means that the output of the function must be  the same
![image](https://user-images.githubusercontent.com/77011982/122585337-63b56180-d029-11eb-8a32-079b143a03c0.png)


My first time looking at the function was confusing as it was more complicated than it needed to be. I ran through various test cases by plugging in different numbers to see what would happen. Turns out for every number you plug in their will always be a sequence that will return the number as there is another blob of data that seems to be ASCII character.
![image](https://user-images.githubusercontent.com/77011982/122585574-a119ef00-d029-11eb-959d-f6db1ba8e6fe.png)
After reading the code more and recreating it in python I finally understood that this function was just grabbing the index of the letter on the blob of ASCII letters. This made so much sense as the function would grab the index and the program would compare the index to an already known list of indexes. 
Thus we just need to grab the ASCII characters and the indexes to get the final flag. 
![image](https://user-images.githubusercontent.com/77011982/122605393-602fd380-d045-11eb-91c1-46a3b298904b.png)
