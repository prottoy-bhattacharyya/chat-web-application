from  flask import Flask
import mysql.connector

app = Flask(__name__)

sql = mysql.connector.connect(
    host="mysql-app",
    user="root",
    password="1234",
    database="test"
)
cursor = sql.cursor()

result = cursor.execute('''select * from test''')
# result = "test"


@app.route('/')
def home():
    return result

app.run(debug=True)
