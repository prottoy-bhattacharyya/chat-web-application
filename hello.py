from flask import Flask, render_template, request, redirect
from datetime import datetime
import mysql.connector

sqldb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="userlogin"
)

cursor = sqldb.cursor()



# class messageDetails:
#     def __init__(self, sender, message, date, seen):
#         self.sender = sender
#         self.message = message
#         self.date = datetime.datetime.now()
#         self.seen = seen
    
username = "admin"
password = "admin"
messages = []

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        global username 
        username = request.form['username']
        global message
        password = request.form['password']

        cursor.execute("SELECT * FROM userLogin WHERE username = %s AND password = %s", (username, password))
        if(cursor.fetchone()):
            return redirect('/chatroom')
        if username == "admin" and password == "admin":
            return redirect('/chatroom')
        else:
            return render_template('login.html',error="Wrong username or password")
    return render_template('login.html')


@app.route('/chatroom', methods=['POST', 'GET'])
def chatroom():
    if request.method == 'POST':
        message = request.form['message']
        messages.append(message)

    return render_template('chatroom.html', username=username, messages=messages)
    
if __name__ == '__main__':
    app.run(debug = True)
    