DROP TABLE IF EXISTS users;
DROP SEQUENCE IF EXISTS user_ids;

CREATE SEQUENCE user_ids;
CREATE TABLE users (id INTEGER PRIMARY KEY DEFAULT NEXTVAL('user_ids'), login CHAR(64), password CHAR(64));

INSERT INTO users (login, password) VALUES ('admin1', 'insecurepass1');
INSERT INTO users (login, password) VALUES ('admin2', 'insecurepass2');
INSERT INTO users (login, password) VALUES ('admin3', 'insecurepass3');