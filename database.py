import mysql.connector as mysql

#Initializing Database for Point Management System

#Format of the SQL table for Point Management System
'''TABLE players(
	wins INT(100),
	first_name VARCHAR(20),
	last_name VARCHAR(20),
	username VARCHAR(20) PRIMARY KEY)'''

conn = mysql.connect(host='localhost',
					 port=8889,
                     user='root',
                     password='password',
                     database = 'pingpong')

cursor = conn.cursor()
cursor.execute("CREATE TABLE players(wins INT(100),first_name VARCHAR(20),last_name VARCHAR(20),username VARCHAR(20) PRIMARY KEY)")
cursor.execute("CREATE TABLE games (player1 VARCHAR(255), player1_points INT(100), player2 VARCHAR(255), player2_points INT(100), roundnum INT(100), winner VARCHAR(255) )")
conn.commit()

cursor.execute("SHOW TABLES")

tables = cursor.fetchall()

print(tables)

cursor.excute("INSERT INTO players (wins, first_name, last_name, username) VALUES (0, jane, doe, jd123)")
cursor.excute("INSERT INTO players (wins, first_name, last_name, username) VALUES (0, john, smith, js789)")

conn.commit()
cursor.close()

