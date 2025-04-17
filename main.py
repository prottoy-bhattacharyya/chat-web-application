from flask import Flask, render_template, request, redirect, url_for
import hashlib
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import meta_llama_AI as meta
import asyncio

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
        except Error as error:
            return render_template('login2.html', error=error)
        if(data):
            try:
                fullName = str(data[2])
            except Error as error:
                return render_template('login2.html', error = error)
            
            return redirect('/chatroom')
        else:
            return render_template('login2.html', error ="Wrong username or password")
        
    return render_template('login2.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        fullName = request.form["fullName"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        try:
            cursor.execute('''SELECT username FROM userinfo
                           WHERE username = %s'''
                           ,(username,))
            if cursor.fetchall:
                return render_template('signup.html', username_error="Username already exist. Try another")
        except mysql.error as error:
            return render_template('signup.html', error=error)

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")
        
        hashed_password = hashPass(password)
        try:
            cursor.execute('''INSERT INTO userinfo
                        VALUES(%s,%s,%s,%s)''',
                        (username,hashed_password,fullName,email))
            sqldb.commit()
        except Error as error:
            return render_template('signup.html', error=error)
        return redirect('/chatroom')
    
    return render_template('signup.html')

@app.route('/chatroom', methods=['POST', 'GET'])
def chatroom():
    cursor.execute('''SELECT fullName FROM userinfo''')
    names = cursor.fetchall()
    return render_template('chatroom.html', names=names, messages=messages)
    

@app.route('/aiChat', methods=['POST','GET'])
def aiChat():
    if request.method == 'POST':

        question = request.form['question']
        if question == "":
            redirect('/aiChat')
        
        html_text = ''' Please format your response using only HTML tags. 
                        For example, use <p> for paragraphs, <strong> for bold text, 
                        <em> for italics, and <ul><li> for lists, 
                        <br> for line breaks and colorful texts
                        and never mention about html tags in your answer'''
        
        try:
            response = meta.metaLlama(question + html_text)
        except Error as error:
            render_template('aiChat.html', error = error)
            
        return render_template('aiChat.html',question = question, response=response)
    return render_template('aiChat.html')
    
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')
    