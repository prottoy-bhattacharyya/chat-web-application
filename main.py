from flask import Flask, render_template, request, redirect
import hashlib
from datetime import datetime
import mysql.connector

sqldb = mysql.connector.connect(
    host="localhost",
    user="root",
    # password="1234",
    database="chat_web_app"
)
cursor = sqldb.cursor()

def hashPass(password):
    bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256(bytes)
    hash = hash_obj.hexdigest()
    return hash


messages = []

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashPass(password)
        try:
            cursor.execute('''SELECT * FROM userinfo 
                        WHERE username = %s AND hashed_password = %s''', 
                        (username, hashed_password))
            data = cursor.fetchone()
        except mysql.connector.Error as error:
            return render_template('login.html', error=error)
        if(data):
            try:
                fullName = str(data[2])
            except mysql.connector.Error as error:
                return render_template('login.html', error = error)
            
            return redirect('/chatroom')
        else:
            return render_template('login.html', error="Wrong username or password")
        
    return render_template('login.html')
@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        fullName = request.form["fullName"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")
        
        hashed_password = hashPass(password)
        try:
            cursor.execute('''INSERT INTO userinfo
                        VALUES(%s,%s,%s,%s)''',
                        (username,hashed_password,fullName,email))
            sqldb.commit()
        except mysql.connector.Error as error:
            return render_template('signup.html', error=error)
        return redirect('/chatroom')
    
    return render_template('signup.html')

@app.route('/chatroom', methods=['POST', 'GET'])
def chatroom():
    cursor.execute('''SELECT fullName FROM userinfo''')
    names = cursor.fetchall()
    return render_template('chatroom.html', names=names, messages=messages)
    
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')
    