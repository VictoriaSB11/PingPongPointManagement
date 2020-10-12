from flask import Flask, request, render_template
import mysql.connector as mysql

#Format of the SQL table for Point Management System
'''TABLE players(
	wins INT(100),
	first_name VARCHAR(20),
	last_name VARCHAR(20),
	username VARCHAR(20) PRIMARY KEY)'''

'''TABLE games (player1 VARCHAR(255), player1_points INT(100), 
				player_two VARCHAR(255), player2_points INT(100), 
				roundnum INT(100), winner VARCHAR(255))'''

app = Flask(__name__)
app.config["DEBUG"] = True

conn = mysql.connect(host='localhost',
					 port=8889,
                     user='root',
                     password='password',
                     database = 'pingpong')

#Methods
@app.route('/')
@app.route('/backHome', methods = ['GET', 'POST'])
def home():
	cursor = conn.cursor()
	query = 'SELECT * FROM players ORDER BY wins DESC'
	cursor.execute(query)
	players = cursor.fetchall()
	conn.commit()
	return render_template('index.html', players=players)

#Home Template
#	Display current leaderboard
#	Ask if want to start a game - Select Opponents

#Method to Register Names in Home Template
#	(First Name, Last Name, Nickname, # Wins)
@app.route('/registerPlayer', methods = ['GET', 'POST'])
def registerPlayer():
	first_name = request.form['fname']
	last_name = request.form['lname']
	username = request.form['uname']
	wins = 0

	cursor = conn.cursor()

	query = "INSERT INTO players (wins, first_name, last_name, username) VALUES (%s, %s, %s, %s)"
	values = (wins, first_name, last_name, username)
	cursor.execute(query, values)
	conn.commit()
	print(cursor.rowcount, " players registered")
	#Does user already exist? Should not be able to register duplicate usernames.. (later)
	#Display on HTML that player was successfully registered? (later)
	return render_template('index.html')

#Game/Round Template (for Entering Points after each round)
#	Choose a server to start (Display server)
#	After round completed (Player manually enter point for player that won the round)
# 	After each round, select other person to serve
#	When a player gets to 10 - Announce winner of the game
#	Go back to Home Page - Display updated leaderboard
@app.route('/startGame', methods = ['GET', 'POST'])
def startGame():
	player1 = request.form['player1']
	player2 = request.form['player2']
	server = request.form['server']

	cursor = conn.cursor()
	query = 'INSERT INTO games (player1, player1_points, player_two, player2_points, roundnum) VALUES (%s, %s, %s, %s, %s)'
	values = (player1, 0, player2, 0, 1)
	cursor.execute(query, values)
	cursor.close()

	#Error check - If player does not exist, prompt user to register a new player (later)
	#Come back to this.. trying to check if user exists in database before proceeding to game.

	return render_template('game.html', player1 = player1, player2 = player2, server = server, roundnum = 0)

def updateWins(player):
	cursor = conn.cursor()
	select_query = 'SELECT wins FROM players WHERE username = %s'
	cursor.execute(select_query, (player,))
	wins = cursor.fetchall()

	if wins is None:
		update_query = 'UPDATE players SET wins = 1 WHERE username = %s'
		cursor.execute(update_query, (player,))
		cursor.close()
	else:
		wins = wins[0][0]
		wins = wins + 1
		update_query = 'UPDATE players SET wins = %s WHERE username = %s'
		cursor.execute(update_query, (wins, player))
		cursor.close()

def updateRound(player1, player2):
	cursor = conn.cursor()
	select_query = 'SELECT roundnum FROM games WHERE player1 = %s AND player_two = %s'
	cursor.execute(select_query, (player1, player2))
	roundnum = cursor.fetchall()

	if roundnum is None:
		update_query = 'UPDATE games SET roundnum = 1 WHERE player1 = %s AND player_two = %s'
		cursor.execute(update_query, (player1, player2))
		cursor.close()
	else:
		roundnum = roundnum[0][0]
		roundnum = roundnum + 1
		update_query = 'UPDATE games SET roundnum = %s WHERE player1 = %s AND player_two = %s'
		cursor.execute(update_query, (roundnum, player1, player2))
		cursor.close()
	return(roundnum)

@app.route('/playGame', methods = ['GET', 'POST'])
def playGame():
	p1 = request.form['player1']
	p2 = request.form['player2']
	s = request.form['server']

	if request.form.get("addpoint1"):
		#Query to get Player 1 points and update
		cursor = conn.cursor()
		select_query = 'SELECT player1_points FROM games WHERE player1 = %s'
		cursor.execute(select_query, (p1,))
		points1 = cursor.fetchall()

		if points1 is None:
			update_query = 'UPDATE games SET player1_points = 1 WHERE player1 = %s'
			cursor.execute(update_query, (p1,))
			cursor.close()
		else:
			points1 = points1[0][0]
			points1 = points1 + 1
			update_query = 'UPDATE games SET player1_points = %s WHERE player1 = %s'
			cursor.execute(update_query, (points1, p1))
			cursor.close()

		#Query to get Player 2 points for display
		cursor = conn.cursor()
		select_query2 = 'SELECT player2_points FROM games WHERE player_two = %s'
		cursor.execute(select_query2, (p2,))
		points2 = cursor.fetchall()
		cursor.close()

		#Function to update round
		roundnum = updateRound(p1, p2)
		if roundnum % 2 == 0:
			if s == p1:
				server = p2
			else:
				server = p1
		else:
			server = s

		if points1 > 10 and points2[0][0] < 10 or points2 is None:
			updateWins(p1)
			return render_template('winner.html', player1 = p1, player2 = p2, winner = p1)

		elif points1 > 10 and points2[0][0] > 10:
			if points1 > 10 and points2[0][0] == points1 - 2:
				updateWins(p1)
				return render_template('winner.html', player1 = p1, player2 = p2, winner = p1)
			else:
				return render_template('game.html', player1 = p1, points1 = points1, player2 = p2, points2 = points2, server = server, roundnum = roundnum)

		else:
			return render_template('game.html', player1 = p1, points1 = points1, player2 = p2, points2 = points2, server = server, roundnum = roundnum)

	elif request.form.get("addpoint2"):
		#Query to get Player 2 points and update
		cursor = conn.cursor()
		select_query = 'SELECT player2_points FROM games WHERE player_two = %s'
		cursor.execute(select_query, (p2,))
		points2 = cursor.fetchall()

		if points2 is None:
			update_query = 'UPDATE games SET player2_points = 1 WHERE player_two = %s'
			cursor.execute(update_query, (p2,))
			cursor.close()
		else:
			points2 = points2[0][0]
			points2 = points2 + 1
			update_query = 'UPDATE games SET player2_points = %s WHERE player_two = %s'
			cursor.execute(update_query, (points2, p2))
			cursor.close()

		#Query to get Player 1 points for display
		cursor = conn.cursor()
		select_query2 = 'SELECT player1_points FROM games WHERE player1 = %s'
		cursor.execute(select_query2, (p1,))
		points1 = cursor.fetchall()
		cursor.close()

		#Function to update round
		roundnum = updateRound(p1, p2)
		if roundnum % 2 == 0:
			if s == p1:
				server = p2
			else:
				server = p1
		else:
			server = s

		if points2 > 10 and points1[0][0] < 10 or points2 is None:
			return render_template('winner.html', player1 = p1, player2 = p2, winner = p1)

		elif points2 > 10 and points1[0][0] > 10:
			if points2 > 10 and points1[0][0] == points2 - 2:
				return render_template('winner.html', player1 = p1, player2 = p2, winner = p1)
			else:
				return render_template('game.html', player1 = p1, points1 = points1, player2 = p2, points2 = points2, server = server, roundnum = roundnum)

		else:
			return render_template('game.html', player1 = p1, points1 = points1, player2 = p2, points2 = points2, server = server, roundnum = roundnum)


if __name__ == '__main__':
	app.run()














