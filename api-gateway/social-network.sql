DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS membership;
DROP TABLE IF EXISTS friendship;

DROP SEQUENCE IF EXISTS user_ids;
DROP SEQUENCE IF EXISTS group_ids;

CREATE SEQUENCE user_ids;
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY DEFAULT NEXTVAL('user_ids'),
    first_name VARCHAR(64),
    last_name VARCHAR(64));

CREATE SEQUENCE group_ids;
CREATE TABLE groups (
    group_id INTEGER PRIMARY KEY DEFAULT NEXTVAL('group_ids'),
    group_name VARCHAR(64));

INSERT INTO users (first_name, last_name) VALUES
    ('John', 'Doe'),
    ('Alice', 'Black'),
    ('Bob', 'White'),
    ('Diana', 'Woods');

INSERT INTO groups (group_name) VALUES
    ('Males'),
    ('Females'),
    ('Geeks');

CREATE TABLE membership (
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL);

CREATE TABLE friendship (
    user_id INTEGER NOT NULL,
    friend_id INTEGER NOT NULL);

INSERT INTO membership (user_id, group_id) VALUES
    (1, 1),
    (2, 2),
    (3, 1),
    (4, 2),
    (2, 3),
    (3, 3);

INSERT INTO friendship(user_id, friend_id) VALUES
    (2, 3),
    (3, 2);