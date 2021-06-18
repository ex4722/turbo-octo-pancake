These two were one of my favorite challenges during the CTF as I learned a lot about web assembly programing. The first challenge was very simple as the flag was in the "binary" sent to the website. Using burp we can intercept the request and grab the binary.
When we send a request for the website we notice that it makes a GET request to /code.wasm. This means we can go their and download the file. Once we download the file we can search for our low hanging fruit such as string. Running strings we see the flag
![image](https://user-images.githubusercontent.com/77011982/122488067-b1d75000-cfaa-11eb-8fd5-dbfc79d54743.png)

For the second challenge it was like the first one but much harder. Once we download the file we see that strings does not work as well as it should. We do see a strange string that looks like 
