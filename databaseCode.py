import mysql.connector
import hashlib
def hashPass(password):
    bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256(bytes)
    hash = hash_obj.hexdigest()
    return hash

db = mysql.connector.connect(
    host="localhost",
    user="root",
    # password="your_password",
    database="chat_web_app"
)

# create user account
# print ("Create user account")
# username = input("Username :")
# password = input("Password :")
# fullName = input("Full Name :")
# email = input("Email :")

# hashed_password = hashPass(password)

# cursor = db.cursor()
# cursor.execute('''INSERT INTO userinfo
#                 VALUES(%s,%s,%s,%s)''',
#                 (username,hashed_password,fullName,email))

# db.commit()

#find user information
print("login")
username = input("Username :")
password = input("Password :")
cursor = db.cursor()
hashed_password = hashPass(password)
cursor.execute('''SELECT * FROM userinfo 
               where username = %s AND hashed_password = %s''', 
               (username,hashed_password))

# res = cursor.fetchall()
# for i in res:
#     print(i)

print(str(cursor.fetchone()[2]))