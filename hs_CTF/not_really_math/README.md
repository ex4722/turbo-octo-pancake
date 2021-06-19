### The main idea of this challenge was to solve custom questions through a netcat connection. Looking at the pdf given we see that we need to solve the given equation but the twist was how the order of operations got flopped and now addition is before multiplication. 
To solve this challenge I decided to use python3 and pwn tools to get a connection and use regex to do magic. 

The whole top section is just boilerplate information to connect to the system and grab the equation. Once I got the equation I used string replacing to replace the a's with + and the m's with \*.

```python
prompt = prompt.replace("m","*")
prompt = prompt.replace("a","+")
```

After getting the equation I needed to solve I was stuck for a while on how to swap the order of operations. I wanted to be lazy and find a way to change how python interacts with PEMDAS but turns out it does not exist. In the end, I just decided to add parentheses around the numbers being added together. I spent a long time figuring out how to make a regex for this as I don't have much experience with it but I'm very happy to say I figured it out. Here the statement:
```re
[(\d+|\(+\d+\+\d+\)+)]+\+[(\d+|\(+\d+\+\d+\)+)]+
```

The basic idea behind this one is to find all possible statements that have any number of parentheses followed by any sized digit followed by any amount of parentheses and a plus sign which then has the first half again. This whole regex is then repeated until there are no more additions sign's not in parentheses. 
Using re from python I just replaced it with itself and parentheses around it. I couldn't figure out the syntax for this but after a lot of stack overflow I found out that you only need to use an r prefix and then \g<0> to replace with itself. 

```python3
prompt = (re.sub("[(\d+|\(+\d+\+\d+\)+)]+\+[(\d+|\(+\d+\+\d+\)+)]+",r"(\g<0>)",prompt))
```

After this, I passed it into eval and then tried to send it in to the connection but somehow I was still getting it wrong. After a lot of debugging and finally asking for a sanity check, the author of the challenge told me to look over the pdf again. Then I saw what I should have saw right away. 

![image](https://user-images.githubusercontent.com/77011982/122651649-2e337580-d108-11eb-9e8c-eafccaf928d2.png)

So the issue was I didn't take the mod of the number and that was the reason it didn't work. After I fixed this I got the flag right away. 
![image](https://user-images.githubusercontent.com/77011982/122651670-4dca9e00-d108-11eb-87e9-ec6e23044e30.png)


``
flag{yknow_wh4t_3ls3_is_n0t_real1y_math?_c00l_m4th_games.com}
``

This was my favorite challenge of the whole CTF as it was a lot of fun to solve and taught me a lot about regex and reminded me to always read the prompt first. 
