from string import ascii_lowercase
import numpy as np

string = list(ascii_lowercase)
def unique(list1):
    x = np.array(list1)
    return (np.unique(x))


f = open("ciphertext.md",'r')
text = (f.read().strip())
text_ord = []
for i in text:
    text_ord.append(ord(i))
unique_char= []
for i in text_ord:
    if  not chr(i).isprintable():
        unique_char.append(i)
unique_char=  unique(unique_char)

dictionary = {}
for i, value in enumerate(unique_char) :
    dictionary[value] = string[i]
for index,key in enumerate(text_ord):
    if key in dictionary:
        text_ord[index] = dictionary[key]
    else:
        text_ord[index] = (chr(key))
print(text_ord)
print(''.join(text_ord))





