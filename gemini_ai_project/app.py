# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime
import meta_llama_AI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' 
socketio = SocketIO(app)


DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'test_chat_app'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(255) NOT NULL,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    dob DATE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sender_id INT NOT NULL,
                    receiver_id INT NOT NULL,
                    message_text TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users(id),
                    FOREIGN KEY (receiver_id) REFERENCES users(id)
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aiChat(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username TEXT NOT NULL,
                    user_id INT NOT NULL,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            """)
            conn.commit()
            print("Database tables created or already exist.")
        except mysql.connector.Error as err:
            print(f"Error creating tables: {err}")
        finally:
            cursor.close()
            conn.close()


with app.app_context():
    init_db()

@app.route('/')
def index():
    
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("""SELECT * FROM users 
                               WHERE username = %s""", (username,))
                user = cursor.fetchone()

                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['full_name'] = user['full_name']
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('Invalid username or password', 'danger')
            except mysql.connector.Error as err:
                print(f"Error during login: {err}")
                flash('An error occurred during login. Please try again.', 'danger')
            finally:
                cursor.close()
                conn.close()
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        dob_str = request.form['dob']
        email = request.form['email']
        password = request.form['password']

        if not all([full_name, username, dob_str, email, password]):
            flash('All fields are required!', 'danger')
            return render_template('signup.html')

        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date of birth format. Please use YYYY-MM-DD.', 'danger')
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (full_name, username, dob, email, password_hash) VALUES (%s, %s, %s, %s, %s)",
                               (full_name, username, dob, email, hashed_password))
                conn.commit()
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            except mysql.connector.Error as err:
                if err.errno == 1062: # Duplicate entry error code
                    flash('Username or Email already exists. Please choose another.', 'danger')
                else:
                    print(f"Error during signup: {err}")
                    flash('An error occurred during signup. Please try again.', 'danger')
            finally:
                cursor.close()
                conn.close()
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('full_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/home')
def home():
    id = session['user_id']
    if not id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT full_name, username, dob, email FROM users WHERE id = %s", (id,))
            user = cursor.fetchone()
            if user:
                full_name = user['full_name']
                username = user['username']
                dob = user['dob'].strftime("%Y-%m-%d")
                email = user['email']
        except mysql.connector.Error as err:
            print(f"Error fetching user data: {err}")
        finally:
            cursor.close()
            conn.close()

    return render_template('home.html', full_name=full_name, username=username, dob=dob, email=email)
@app.route('/chat')
def chat():

    if 'user_id' not in session:
        flash('Please log in to access the chat.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    users = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, full_name, username FROM users WHERE id != %s", (session['user_id'],))
            users = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error fetching users: {err}")
        finally:
            cursor.close()
            conn.close()

    return render_template('chat.html', current_user_id=session['user_id'],
                           current_username=session['username'],
                           current_full_name=session['full_name'],
                           users=users)

@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        user_id = session['user_id']
        username = session['username']
        join_room(str(user_id))
        print(f"User {username} (ID: {user_id}) connected and joined room {user_id}")
        emit('user_status', {'user_id': user_id, 'status': 'online'}, broadcast=True)
    else:
        print("Unauthenticated user tried to connect to SocketIO.")
        return False

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        user_id = session['user_id']
        username = session['username']
        leave_room(str(user_id))
        print(f"User {username} (ID: {user_id}) disconnected.")
        emit('user_status', {'user_id': user_id, 'status': 'offline'}, broadcast=True)

@socketio.on('send_message')
def handle_send_message(data):
    if 'user_id' not in session:
        print("Unauthenticated user tried to send message.")
        return

    sender_id = session['user_id']
    receiver_id = data.get('receiver_id')
    message_text = data.get('message')
    sender_username = session['username']

    if not all([receiver_id, message_text]):
        print("Missing receiver_id or message_text in send_message data.")
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO messages (sender_id, receiver_id, message_text) VALUES (%s, %s, %s)",
                           (sender_id, receiver_id, message_text))
            conn.commit()

            cursor.execute("SELECT timestamp FROM messages WHERE id = LAST_INSERT_ID()")
            timestamp = cursor.fetchone()[0].strftime('%Y-%m-%d %I:%M:%S %p')

            emit('receive_message', {
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'message': message_text,
                'timestamp': timestamp,
                'sender_username': sender_username
            }, room=str(sender_id))

            if str(receiver_id) != str(sender_id):
                emit('receive_message', {
                    'sender_id': sender_id,
                    'receiver_id': receiver_id,
                    'message': message_text,
                    'timestamp': timestamp,
                    'sender_username': sender_username
                }, room=str(receiver_id))

            print(f"Message from {sender_username} (ID: {sender_id}) to {receiver_id}: {message_text}")

        except mysql.connector.Error as err:
            print(f"Error saving message: {err}")
        finally:
            cursor.close()
            conn.close()

@socketio.on('request_chat_history')
def handle_request_chat_history(data):
    if 'user_id' not in session:
        print("Unauthenticated user tried to request chat history.")
        return

    user1_id = session['user_id']
    user2_id = data.get('other_user_id')

    if not user2_id:
        print("Missing other_user_id in request_chat_history data.")
        return

    conn = get_db_connection()
    history = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT m.sender_id, m.receiver_id, m.message_text, m.timestamp, u.username as sender_username
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
                ORDER BY timestamp ASC
            """, (user1_id, user2_id, user2_id, user1_id))

            history = cursor.fetchall()
            for msg in history:
                msg['timestamp'] = msg['timestamp'].strftime('%Y-%m-%d %I:%M:%S %p')

            emit('chat_history', {'other_user_id': user2_id, 'history': history}, room=str(user1_id))
            print(f"Sent chat history for user {user2_id} to {session['username']} (ID: {user1_id}).")

        except mysql.connector.Error as err:
            print(f"Error fetching chat history: {err}")
        finally:
            cursor.close()
            conn.close()

@app.route('/aiChat', methods=['POST','GET'])
def aiChat():
    return render_template('aiChat.html')

@socketio.on('connect', namespace='/aiChat')
def ai_connect():
    username = session['username']
    user_id = session['user_id']
    join_room(str(user_id), namespace='/aiChat')
    print(f"AI Chat: User '{username}' (ID: {user_id}) connected.")

@socketio.on('ai_from_client', namespace='/aiChat')
def ai_from_client(data):
    user_id = session['user_id']
    username = session['username']
    prompt = data.get('prompt')
    
    if user_id and prompt:
        try:
            response = meta_llama_AI.metaLlama(prompt, user_id, username)
            print(f"AI chat: {username}:{prompt} ==> {response}")
            emit('ai_from_server', {'response': response}, room=str(user_id), namespace='/aiChat')
        except Exception as e:
            print(f"ERROR: AI Chat: Exception in meta.metaLlama or during emit: {e}")
            emit('ai_from_server', {'response': f'Error processing AI request: {e}'}, room=str(user_id), namespace='/aiChat')
    else:
        print(f"AI Chat: Missing user_id ({user_id}) or prompt ({prompt}).")
        emit('ai_from_server', {'response': 'Error: Invalid request or not connected properly.'}, room=str(user_id), namespace='/aiChat')
    
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
