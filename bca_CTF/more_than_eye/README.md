This was a very fun challenge as I was a little stuck on this challenge until i decided to to pipe it into xxd so see what was going on. 
![image](https://user-images.githubusercontent.com/77011982/122487085-615ef300-cfa8-11eb-9ea8-3e4650cf4183.png)

This showed that their were two characters that were being repeated over and over again, thus i assumed that they were binary so i opened the file in vim.
In vim it was very obvious what was going on 
![image](https://user-images.githubusercontent.com/77011982/122487127-7f2c5800-cfa8-11eb-8365-750112722e68.png)
Using some vim magic I was able to conver the <200b> to 0 and <200c> to 1
```vim 
:%s/<200b>/0/g                                                                                                 
:%s/<200c>/1/g                                                                                                 
```

Afterwards we get a binary sequence that looks something like this
``011000100110001101100001011000110111010001100110011110110111101000110011011100100011000001011111011101110011000101100100011101000110100001011111011010100111010101101110011001110110110000110011010111110110101000111000001100100110000101111000010010000011010001111101``
Then I just tossed it into cyberchef and then we get our flag!
![image](https://user-images.githubusercontent.com/77011982/122487310-f4982880-cfa8-11eb-8681-66fd68ad726c.png)
