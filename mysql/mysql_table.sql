CREATE DATABASE chat_web_app;

USE chat_web_app;

CREATE TABLE userinfo(
	username VARCHAR(10) PRIMARY KEY,
  	hashed_password VARCHAR(100),
  	fullName TEXT,
 	email TEXT
);

CREATE TABLE conversation(
	user1 VARCHAR(10),
	user1_msg TEXT,
	user2 VARCHAR(10),
	user2_msg TEXT,
	time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE aiChat(
	id INT AUTO_INCREMENT PRIMARY KEY,
  	username VARCHAR(10),
	user_msg TEXT,
    ai_msg TEXT,
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
