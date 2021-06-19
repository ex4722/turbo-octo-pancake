from pwn import *
import re 
s = remote("not-really-math.hsc.tf", 1337)
(s.recvuntil(':'))
prompt = (s.recvuntil(':')).decode()
prompt = (re.findall("\n.*\n",prompt))
prompt = prompt[0]
prompt = (prompt.strip())
prompt = prompt.replace("m","*")
prompt = prompt.replace("a","+")
print(prompt)
prompt = (re.sub("[(\d+|\(+\d+\+\d+\)+)]+\+[(\d+|\(+\d+\+\d+\)+)]+",r"(\g<0>)",prompt))
print(prompt)
print(eval(prompt))
s.sendline(str(eval(prompt)))
print("Finished:1")


for i in range(1,100):
    prompt = (s.recvline().decode())
    print(f"Unfiltered:{prompt}")
    if 'Unfortunately,' in prompt:
        print("Failed")
        break
    if "flag" in prompt:
        print(prompt)
        break
    prompt = (re.findall(r"[\d+(a|m)\d+]+",prompt)[0])
    print(f"Grepping only:{prompt}")
    prompt = prompt.replace("m","*")
    prompt = prompt.replace("a","+")
    prompt = (re.sub("[(\d+|\(+\d+\+\d+\)+)]+\+[(\d+|\(+\d+\+\d+\)+)]+",r"(\g<0>)",prompt))
    print(f"After regex: {prompt}")
    answer = (eval(prompt))
    answer = answer % 4294967295
    s.sendline(str(answer))
    print(f"Answer: {answer}")
    print(f"Finished: {i+1}")
