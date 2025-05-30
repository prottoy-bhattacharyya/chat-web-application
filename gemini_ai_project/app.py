# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # Replace with a strong, random secret key
socketio = SocketIO(app)

# Database configuration (replace with your MySQL credentials)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'test_chat_app'
}

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def init_db():
    """Initializes the database by creating tables if they don't exist."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(255) NOT NULL,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    dob DATE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                )
            """)
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sender_id INT NOT NULL,
                    receiver_id INT NOT NULL,
                    message_text TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users(id),
                    FOREIGN KEY (receiver_id) REFERENCES users(id)
                )
            """)
            conn.commit()
            print("Database tables created or already exist.")
        except mysql.connector.Error as err:
            print(f"Error creating tables: {err}")
        finally:
            cursor.close()
            conn.close()

# Call init_db to ensure tables are created when the app starts
with app.app_context():
    init_db()

@app.route('/')
def index():
    """Renders the login page. Redirects to chat if already logged in."""
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if 'user_id' in session:
        return redirect(url_for('chat'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT id, username, password_hash, full_name FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['full_name'] = user['full_name']
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('chat'))
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
    """Handles user registration."""
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        dob_str = request.form['dob']
        email = request.form['email']
        password = request.form['password']

        # Basic validation
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
    """Logs out the current user."""
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('full_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    """Renders the chat page. Requires user to be logged in."""
    if 'user_id' not in session:
        flash('Please log in to access the chat.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    users = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Fetch all users except the current one to display as friends
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
    """Handles new client connections."""
    if 'user_id' in session:
        user_id = session['user_id']
        username = session['username']
        # Join a room specific to the user's ID for private messaging
        join_room(str(user_id))
        print(f"User {username} (ID: {user_id}) connected and joined room {user_id}")
        # Optionally, emit an online status to all connected clients
        emit('user_status', {'user_id': user_id, 'status': 'online'}, broadcast=True)
    else:
        print("Unauthenticated user tried to connect to SocketIO.")
        return False # Reject unauthenticated connections

@socketio.on('disconnect')
def handle_disconnect():
    """Handles client disconnections."""
    if 'user_id' in session:
        user_id = session['user_id']
        username = session['username']
        leave_room(str(user_id))
        print(f"User {username} (ID: {user_id}) disconnected.")
        # Optionally, emit an offline status to all connected clients
        emit('user_status', {'user_id': user_id, 'status': 'offline'}, broadcast=True)

@socketio.on('send_message')
def handle_send_message(data):
    """Handles incoming chat messages and saves them to the database."""
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
            # Save message to database
            cursor.execute("INSERT INTO messages (sender_id, receiver_id, message_text) VALUES (%s, %s, %s)",
                           (sender_id, receiver_id, message_text))
            conn.commit()

            # Get the timestamp of the saved message
            cursor.execute("SELECT timestamp FROM messages WHERE id = LAST_INSERT_ID()")
            timestamp = cursor.fetchone()[0].strftime('%Y-%m-%d %H:%M:%S')

            # Emit message to sender's room
            emit('receive_message', {
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'message': message_text,
                'timestamp': timestamp,
                'sender_username': sender_username
            }, room=str(sender_id))

            # Emit message to receiver's room (if receiver is online)
            if str(receiver_id) != str(sender_id): # Don't send twice if chatting with self (not typical for chat app)
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
    """Fetches and sends chat history between two users."""
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
            # Fetch messages where sender is user1 and receiver is user2, OR vice versa
            cursor.execute("""
                SELECT m.sender_id, m.receiver_id, m.message_text, m.timestamp, u.username as sender_username
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
                ORDER BY timestamp ASC
            """, (user1_id, user2_id, user2_id, user1_id))
            history = cursor.fetchall()
            # Format timestamps for display
            for msg in history:
                msg['timestamp'] = msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

            emit('chat_history', {'other_user_id': user2_id, 'history': history}, room=str(user1_id))
            print(f"Sent chat history for user {user2_id} to {session['username']} (ID: {user1_id}).")

        except mysql.connector.Error as err:
            print(f"Error fetching chat history: {err}")
        finally:
            cursor.close()
            conn.close()


if __name__ == '__main__':
    # Run the Flask app with SocketIO
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
