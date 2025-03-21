# import mysql.connector

# sql = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     #password="your_password",
#     database="test"
# )
# cursor = sql.cursor()
# dbName = "chat1"

# cursor.execute(f"""create table {dbName}
#                (sender VARCHAR(255), 
#                 message VARCHAR(255), 
#                 date VARCHAR(10), 
#                 seen BOOLEAN);"""
#             )

# sql.commit()

# for x in cursor:
#     print(x)

from flask import Flask, render_template, request, redirect

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def test1():
    if request.method == 'POST':
        return redirect('/test2')
    else:
        return render_template('test1.html')

@app.route('/test2', methods=['GET', 'POST'])
def test2():
    if request.method == 'POST':
        return redirect('/')
    return render_template('test2.html')

if __name__ == '__main__':
    app.run(debug=True)
    