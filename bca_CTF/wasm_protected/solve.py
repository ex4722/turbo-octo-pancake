from pwn import *
a = [  0x62, 0x6a, 0x73, 0x78, 0x50, 0x4b, 0x4d, 0x48, 0x7c, 0x22, 0x37, 0x4e, 
  0x1b, 0x44, 0x04, 0x33, 0x62, 0x5d, 0x50, 0x52, 0x19, 0x65, 0x25, 0x7f, 
  0x2f, 0x3b, 0x17]
input = []
output = ''
for i in range(len(a)):
    input.append(chr(a[i]^(i*9 & 127)))
    if 0 == i-1+a[i]:
        print("broke")
        break

for i in input:
    output += i
print(output)
'''
for i in range(27):
    if a[i] != input[i]^i*9:
        break
    if 0 != i-1+a:       # Could be input as well
        break
j = c ^ 1*9 
s = a ^ 2*9 
'''
