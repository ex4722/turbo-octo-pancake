##### This was a simple flag checker that was very simple as the flag was already in the data. Using Ghidra to disassemble the code we see that this function takes the user input and runs a function to check each letter of the input. On thing is that this function does not check the length, his means that we can brute force each character one at a time to get the flag without reading the validated code

![image](https://user-images.githubusercontent.com/77011982/122580842-66618800-d024-11eb-8c81-c4b493dc6614.png)

Using a simple iterator over each character and looping over each character in strings we can get the final flag. This is a local binary so it runs very fast. 

![image](https://user-images.githubusercontent.com/77011982/122581080-ade81400-d024-11eb-86b9-a898e7ce83f0.png)


The validate function itself could also be disassembled and we see that each character of the flag is stored in a variable. We could just grab the whole thing and use some more vim magic and cut it up so that we only have a hex string. 

![image](https://user-images.githubusercontent.com/77011982/122581437-0b7c6080-d025-11eb-9bda-c7eb952222ba.png)
