from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import join_room, leave_room, emit, SocketIO
import hashlib 
from datetime import datetime 
import mysql.connector
from mysql.connector import Error
import meta_llama_AI as meta



sqldb = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="1234",
    database="chat_web_app"
)
cursor = sqldb.cursor()

def hashPass(password):
    bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256(bytes)
    hash = hash_obj.hexdigest()
    return hash

sid_map = {}

app = Flask(__name__)
app.config["SECRET_KEY"] = "hello_dear"
Socketio = SocketIO(app)

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
            return render_template('login.html', error=error)
        
        if(data):
            try:
                fullName = str(data[2])
            except Error as error:
                return render_template('login.html', error = error)
            
            session["username"] = username

            return redirect('/chatroom')
        else:
            return render_template('login.html', error ="Wrong username or password")
        
    return render_template('login.html')

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
            result = cursor.fetchall() 
            if result:
                return render_template('signup.html', username_error="Username already exist. Try another")
        except Error as error:
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
        session["username"] = username
        return redirect('/chatroom')
    
    return render_template('signup.html')


@app.route('/chatroom', methods=['POST', 'GET'])
def chatroom():
    if not session.get("username"):
        return redirect('/')
    cursor.execute('''SELECT fullName FROM userinfo''')
    names = cursor.fetchall()
    username = session.get("username")

    return render_template('chatroom.html', names=names)


@Socketio.on("from_client" , namespace='/chatroom')
def message(data):
    sender_name = session.get("username")
    receiver_name = data.get('receiver_name')
    receiver_sid = sid_map.get(receiver_name)
    received_msg = data.get('msg')

    if receiver_name and sender_name and received_msg:
        print(f"{sender_name}--->{receiver_name}: {received_msg}")
        emit('from_server', {'sender': sender_name, 'msg': received_msg}, room=received_msg, namespace='/chatroom')
    

@Socketio.on("connect", namespace='/chatroom')
def connect():
    username = session.get('username')
    if username:
        join_room(username, namespace='/chatroom')
        sid_map[username] = request.sid
        print(f"{username} [{request.sid}] joined")

@Socketio.on('disconnect', namespace='/chatroom')
def disconnect():
    username = session.get('username')
    print(f"{username} leaved")
    leave_room(username, namespace='/chatroom')


@app.route('/aiChat', methods=['POST','GET'])
def aiChat():
    name = session.get("username")
    return render_template('aiChat.html')

@Socketio.on("connect", namespace='/aiChat')
def ai_connect():
    username = session.get('username')
    if username:
        join_room(username, namespace='/aiChat')
        sid_map[username] = request.sid
        print(f"{username} [{request.sid}] joined in aiChat")

@Socketio.on("ai_from_client", namespace='/aiChat')
def ai_message(data):
    sender_name = session.get("username")
    print(sender_name)
    sender_sid = sid_map.get(sender_name)
    print(sender_sid)
    prompt = data.get('prompt')
    print(f"{sender_name}: {prompt}")
    if sender_name and prompt:
        response = meta.metaLlama(prompt, sender_name)
        print(f"{sender_name}--->{prompt}: {response}")
        emit('ai_from_server', {'response': response}, room=sender_sid, namespace='/aiChat')

@Socketio.on('disconnect', namespace='/aiChat')
def ai_disconnect():
    username = session.get('username')
    print(f"{username} leaved from aiChat")
    leave_room(username, namespace='/aiChat')

if __name__ == '__main__':
    Socketio.run(app, debug=True, host='0.0.0.0')
    