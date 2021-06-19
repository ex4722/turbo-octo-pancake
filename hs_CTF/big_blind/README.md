This challenge was a simple SQL injection but the main twist was that it didn't show anything so you only thing you could do was a time-based attack. This was also the challenge I spent almost the whole CTF trying to solve as I couldn't get a working payload to enumerate table names. 
There was the option to use sqlmap to get the flag but I figured since I never made my own script I probably should attempt my own.
The top of the script is just boilerplate information to connect and get a login request. The script worked just fine for the most part and I was able to grab a couple of things. The payloads I used can be found on the payload all the things page https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/MySQL%20Injection.md#mysql-blind-with-substring-equivalent. 
For example these two payloads both worked but they never gave me the full list of tables. 
```python
statement =f"' OR (SELECT substr(database(),1,{len(value)+1})='{value + chr}' AND SLEEP(4))"
statement =f"' OR (SELECT substr(user(),1,{len(value)+1})='{value + chr}' AND SLEEP(4))"
```

I spent a long time trying to get the payload to work and on the last day of the CTF I gave up and just waited out the CTF. Afterward, the challenge creator informed me that turns out my payload was almost correct as all I needed to do was replace database() in the first payload to pass and it should have given the flag. This confused me a lot as the table was never specified. 
```sql
' OR (SELECT substr(pass,1,{len(value)+1})='{value + chr}' AND SLEEP(4))"
```

Anyways the code worked just fine and after running the code we are rewarded with the flag
![image](https://user-images.githubusercontent.com/77011982/122654255-33002580-d118-11eb-8d1e-964011ecda26.png)



However, the better payload would be the one payload on payload all the things that I didn't try
```SQL
' OR (SELECT (CASE WHEN EXISTS(SELECT name FROM items WHERE name REGEXP "^a.*") THEN SLEEP(3) ELSE 1 END)); -- -
```

After modifications, the payload should be more like 
```SQL 
' OR (SELECT (CASE WHEN EXISTS(SELECT pass FROM users WHERE pass REGEXP "^a.*") THEN SLEEP(3) ELSE 1 END)); -- -
```

Both of these would work but I still have no idea why the first one would work. 


``
flag{any_info_is_good_info}
``
