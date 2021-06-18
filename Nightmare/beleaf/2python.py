from pwn import *

user_inp = 'string'

data1 = "wf{_ny}blr"
def checker(letter):
    ite = 0
    # The idea of data1 is not a varible but adress, you add 4 to it for each iterator its on.
    while ite != -1 && letter != data1+ ite*4:
        if ord(letter) < data1 + ite *4:
            ite = ite*2 + 4
        else:
            if data1 + ite *4 < ord(letter):
                ite = (ite +1)* 2
        return ite




data = 0
for i in user_inp:
    var1 = checker(i)
    if var1 != data + i*8:
        print("wrong")
        break

