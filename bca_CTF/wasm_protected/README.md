# Wasm Protected 1&2
These two were some of my favorite challenges during the CTF as I learned a lot about web assembly programing. The first challenge was very simple as the flag was in the "binary" sent to the website. Using burp we can intercept the request and grab the binary.
When we send a request for the website we notice that it makes a GET request to /code.wasm. This means we can go there and download the file. Once we download the file we can search for our low-hanging fruit such as string. Running strings we see the flag
![image](https://user-images.githubusercontent.com/77011982/122488067-b1d75000-cfaa-11eb-8fd5-dbfc79d54743.png)

For the second challenge, it was like the first one but much harder. Once we download the file we see that strings do not work at all. We do see a strange string that looks like a xored string. 
![image](https://user-images.githubusercontent.com/77011982/122488280-23af9980-cfab-11eb-9264-c05b94a5191a.png)
Thus my first instinct was the grab the string and then brute-force it by XORing it with all the possible characters. Sadly this didn't work so I decided I had to read the code of the file itself. After some research on about wasm, I found that we can run a decompiler to get the actual instructions. Reading this file it's very similar to assembly with its jump instructions but being lazy I decided to search for a way to convert .wasm files to C code. To my surprise I found out about a program called wasm-decompile from the wabt package. Running this code generated a very understandable c code. 
![image](https://user-images.githubusercontent.com/77011982/122488587-c49e5480-cfab-11eb-8c7b-f412a0567a29.png)
The general gist is that the string we entered is indeed xored by another string but instead of being xored by a fixed constant it's xored by the product of its index and 9. The & 127 threw me off as I didn't figure out what it was, I just ignored it at first and this caused my script to only return the first half of the flag. After the competition ended however someone pointed out that it's the AND instruction. This was something that I never thought about but you actually just convert both strings to binary and keep all the characters that show up in both. Thus I was able to just use the python built-in function of & to get the flag. 

![image](https://user-images.githubusercontent.com/77011982/122488826-48f0d780-cfac-11eb-903d-3e616ee21cb3.png)


