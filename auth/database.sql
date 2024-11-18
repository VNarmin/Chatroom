drop table if exists users;
-- Query OK, 0 rows affected (0.03 sec) --

create table users (
user_ID int auto_increment primary key,
username varchar(60) not null,
password varchar(60) not null
);
-- Query OK, 0 rows affected (0.03 sec) --

insert into users (username, password)
values ("admin", "admin123");
-- Query OK, 1 row affected (0.00 sec) --

drop table if exists rooms;
-- Query OK, 0 rows affected (0.01 sec) --

create table rooms (
room_ID int auto_increment primary key,
room_name varchar(60) not null,
room_description varchar(240),
room_password varchar(60),
created_at timestamp default current_timestamp
);
-- Query OK, 0 rows affected (0.02 sec) --

insert into rooms (room_name, room_description, room_password) values
("test", "Welcome to our Chatroom!", "test5");
-- Query OK, 1 row affected (0.01 sec) --