from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import join_room, leave_room, emit, SocketIO # Import SocketIO class itself
import hashlib
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import meta_llama_AI as meta 

# --- Database Connection ---
sqldb = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="1234",
    database="chat_web_app"
)
cursor = sqldb.cursor()

# --- Utility Function ---
def hashPass(password):
    bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256(bytes)
    hash_val = hash_obj.hexdigest() 
    return hash_val

# --- Global Data Structures ---
sid_map = {} # Maps usernames to SocketIO SIDs

app = Flask(__name__)
app.config["SECRET_KEY"] = "hello_dear" 
socketio = SocketIO(app)

# --- Routes ---
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
            print(f"DB Error during login: {error}") 
            return render_template('login.html', error=f"Database error: {error}")

        if data:
            session["username"] = username 
            print(f"User '{username}' logged in successfully.")
            return redirect('/chatroom')
        else:
            print(f"Login failed for username: {username}")
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

        try:
            cursor.execute('''SELECT username FROM userinfo
                            WHERE username = %s''',
                            (username,))
            result = cursor.fetchall()
            if result:
                return render_template('signup.html', username_error="Username already exist. Try another")
        except Error as error:
            print(f"DB Error during signup (username check): {error}")
            return render_template('signup.html', error=f"Database error: {error}")

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")

        hashed_password = hashPass(password)
        try:
            cursor.execute('''INSERT INTO userinfo
                            VALUES(%s,%s,%s,%s)''',
                            (username, hashed_password, fullName, email))
            sqldb.commit()
            print(f"User '{username}' signed up successfully.")
        except Error as error:
            print(f"DB Error during signup (insert): {error}")
            return render_template('signup.html', error=f"Database error: {error}")

        session["username"] = username
        return redirect('/chatroom')

    return render_template('signup.html')

@app.route('/chatroom', methods=['POST', 'GET'])
def chatroom():
    if not session.get("username"):
        print("DEBUG: Redirecting to login, no username in session for /chatroom.")
        return redirect('/')
    try:
        cursor.execute('''SELECT fullName FROM userinfo''')
        names = cursor.fetchall()
    except Error as error:
        print(f"DB Error getting full names: {error}")
        names = []
    username = session.get("username")
    print(f"DEBUG: User '{username}' accessing /chatroom.")
    return render_template('chatroom.html', names=names, username=username)

@app.route('/aiChat', methods=['POST','GET'])
def aiChat():
    if not session.get("username"):
        print("DEBUG: Redirecting to login, no username in session for /aiChat.")
        return redirect('/')
    username = session.get("username")
    print(f"DEBUG: User '{username}' accessing /aiChat.")
    return render_template('aiChat.html', username=username)

# --- Chatroom Namespace SocketIO Handlers ---
@socketio.on("connect", namespace='/chatroom')
def chatroom_connect():
    username = session.get('username')
    if username:
        join_room(username, namespace='/chatroom')
        sid_map[username] = request.sid
        print(f"DEBUG: Chatroom: User '{username}' [{request.sid}] joined.")
    else:
        print(f"DEBUG: Chatroom: Unauthenticated client connected with SID: {request.sid}. No username in session.")

@socketio.on("from_client" , namespace='/chatroom')
def message(data):
    sender_name = session.get("username")
    receiver_name = data.get('receiver_name')
    received_msg = data.get('msg')

    print(f"DEBUG: Chatroom: Received message from '{sender_name}' to '{receiver_name}': '{received_msg}'")

    if sender_name and receiver_name and received_msg:
        receiver_sid = sid_map.get(receiver_name)
        if receiver_sid:
            print(f"DEBUG: Chatroom: Emitting to receiver '{receiver_name}' (SID: {receiver_sid}).")
            # Emit to the receiver's room/SID
            emit('from_server', {'sender': sender_name, 'msg': received_msg}, room=receiver_sid, namespace='/chatroom')
            # Optionally emit back to the sender for their own chat history
            emit('from_server', {'sender': sender_name, 'msg': received_msg}, room=request.sid, namespace='/chatroom')
        else:
            print(f"DEBUG: Chatroom: Receiver '{receiver_name}' not found in sid_map or not connected.")
            emit('from_server', {'sender': 'System', 'msg': f"User '{receiver_name}' is not online."}, room=request.sid, namespace='/chatroom') # Notify sender
    else:
        print(f"DEBUG: Chatroom: Incomplete message data from '{sender_name}'. Data: {data}")

@socketio.on('disconnect', namespace='/chatroom')
def chatroom_disconnect():
    username = session.get('username')
    if username:
        print(f"DEBUG: Chatroom: User '{username}' [{request.sid}] disconnected.")
        leave_room(username, namespace='/chatroom')
    else:
        print(f"DEBUG: Chatroom: Unknown client [{request.sid}] disconnected.")

# --- AI Chat Namespace SocketIO Handlers ---
@socketio.on("connect", namespace='/aiChat')
def ai_connect():
    username = session.get('username')
    if username:
        join_room(username, namespace='/aiChat') 
        sid_map[username] = request.sid
        print(f"DEBUG: AI Chat: User '{username}' [{request.sid}] joined.")
    else:
        print(f"DEBUG: AI Chat: Unauthenticated client connected with SID: {request.sid}. No username in session.")


@socketio.on("ai_from_client", namespace='/aiChat') 
def ai_message(data):
    sender_name = session.get("username")
    sender_sid = sid_map.get(sender_name) 
    prompt = data.get('prompt')

    print(f"DEBUG: AI Chat: Received message from '{sender_name}' (SID: {request.sid}) with prompt: '{prompt}'")
    print(f"DEBUG: AI Chat: Sender SID from map: {sender_sid}") # Should match request.sid if only one tab

    if sender_name and prompt and sender_sid: 
        try:
            response = meta.metaLlama(prompt, sender_name)
            print(f"DEBUG: AI Chat: metaLlama response: '{response}'")
            emit('ai_from_server', {'response': response}, room=sender_sid, namespace='/aiChat')
            print(f"DEBUG: AI Chat: Emitted 'ai_from_server' to SID: {sender_sid}.")
        except Exception as e:
            print(f"ERROR: AI Chat: Exception in meta.metaLlama or during emit: {e}")
            emit('ai_from_server', {'response': f'Error processing AI request: {e}'}, room=request.sid, namespace='/aiChat')
    else:
        print(f"DEBUG: AI Chat: Missing sender_name ({sender_name}), prompt ({prompt}), or sender_sid ({sender_sid}).")
        emit('ai_from_server', {'response': 'Error: Invalid request or not connected properly.'}, room=request.sid, namespace='/aiChat')


@socketio.on('disconnect', namespace='/aiChat')
def ai_disconnect():
    username = session.get('username')
    if username:
        print(f"DEBUG: AI Chat: User '{username}' [{request.sid}] disconnected.")
        leave_room(username, namespace='/aiChat')
    else:
        print(f"DEBUG: AI Chat: Unknown client [{request.sid}] disconnected.")


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')