This challenge was a very simple overwriting value below the stack.
Looking at the source code we see that our goal is to get the score to be equal to 0x73434241 which when converted to ASCII and the endianness is swapped its ABCs
![image](https://user-images.githubusercontent.com/77011982/122483069-c235fd80-cf9f-11eb-9170-b54bb2eed2e8.png)
Hmm, how we can change the value of the score? We just need to look a little above this code and we will see this 
![image](https://user-images.githubusercontent.com/77011982/122483124-e2fe5300-cf9f-11eb-9501-4702d24e2804.png)
Basically this just checks the values against an already defined string of the whole alphabet.
If we enter the right string we get a 5 and for each character we miss we lose more points. The real solution however lies not in this but how the stack is ordered.
For example, if we try to pipe in a bunch of AAAAA's into the program we get 
![image](https://user-images.githubusercontent.com/77011982/122483397-76378880-cfa0-11eb-9074-822f2ec766e3.png)

So this means that we a certain offset we overwrite the value of the stored score and thus we can set it to a string to get the flag.
After a little fumbling we see that 
![image](https://user-images.githubusercontent.com/77011982/122483536-d29aa800-cfa0-11eb-9fc3-dadbc5340c89.png)

This means that we need to write 76 characters and then write in the string ABCs at the location of the variable score. 
Normally I would use python3 for this but after learning that python3 cant pipe raw bytes as well I switched Perl

The final payload would be something like this ``perl -e 'print "A" x 76 . "ABCs\n"'| nc bin.bcactf.com 49154 `` and then we see the flag after the college board integrity policy
![image](https://user-images.githubusercontent.com/77011982/122483982-c236fd00-cfa1-11eb-835d-67c3a6c773dd.png)
