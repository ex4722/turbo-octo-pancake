from pwn import *
from string import ascii_letters, digits, punctuation
alphabet = list(ascii_letters+ digits+ punctuation)
alphabet
flag = ''
# Fuzz each character of the flag and build it up
while flag[-1] != '}':
    for ch in alphabet:
        t = process("./rev")
        context.log_level = 'error'
        (t.recvuntil('ya?'))
        t.sendline(f'{flag+ch}')
        print(f"{flag+ch}")
        t.recvline()
        output = t.recvline().decode('utf-8')
        if "this way" in output:
            flag += ch
            break
        t.close()
print(flag)
# Second method using some vim magic we can cutup the bytes found
flag = "\x66\x6c\x61\x67\x7b\x48\x75\x43\x66\x5f\x6c\x41\x62\x7d"
print(flag)
# A harder version of the second method
hex_of_flag = [0x66,0x6c,0x61,0x67,0x7b,0x48,0x75,0x43,0x66,0x5f,0x6c,0x41,0x62,0x7d]
flag = ''
for i in hex_of_flag:
    flag += (chr((i)))
print(flag)
