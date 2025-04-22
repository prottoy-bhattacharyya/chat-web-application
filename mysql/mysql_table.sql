create database chat_web_app;

use chat_web_app;

create table userinfo(
	username varchar(10) primary key,
  hashed_password varchar(100),
  fullName varchar(50),
  email varchar(20)
);

create table aiChat(
	id INT auto_increment primary KEY,
	user_msg TEXT,
    ai_msg TEXT,
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

