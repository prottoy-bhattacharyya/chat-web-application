CREATE DATABASE chat_web_app;

USE chat_web_app;

CREATE TABLE userinfo(
	username VARCHAR(10) PRIMARY KEY,
  	hashed_password VARCHAR(100),
  	fullName TEXT,
 	email TEXT
);

CREATE TABLE conversation(
	from_user VARCHAR(10),
	msg TEXT,
	to_user VARCHAR(10),
	time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE aiChat(
	id INT AUTO_INCREMENT PRIMARY KEY,
  	username TEXT,
	prompt TEXT,
    response TEXT,
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
