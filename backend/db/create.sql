DROP TABLE comments;
DROP TABLE posts;
DROP TABLE groups_to_users;
DROP TABLE group_requests;
DROP TABLE groups;
DROP TABLE messages;
DROP TABLE friends;
DROP TABLE friend_requests;
DROP TABLE profiles;
DROP TABLE users;
CREATE TABLE IF NOT EXISTS users (
  user_id SERIAL PRIMARY KEY NOT NULL,
  username VARCHAR(50) NOT NULL,
  password VARCHAR(225) NOT NULL,
  email VARCHAR(50) NOT NULL,
  name VARCHAR(100),
  first_login BOOLEAN DEFAULT FALSE,
  avatar_url TEXT
);

CREATE TABLE IF NOT EXISTS profiles (
  user_id INT PRIMARY KEY NOT NULL,
  bio VARCHAR(200),
  avatar_url TEXT,
  location VARCHAR(50),
  conditions TEXT[],
  status VARCHAR(20) CHECK (status in ('Patient', 'Caregiver')) DEFAULT 'Patient',
  interests TEXT[],
  private BOOLEAN,
  FOREIGN KEY (user_id) REFERENCES users (user_id)
);


CREATE TABLE IF NOT EXISTS friend_requests (
  request_id SERIAL PRIMARY KEY,
  sender_id INT NOT NULL,
  receiver_id INT NOT NULL,
  requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(20) CHECK (status in ('pending', 'accepted', 'rejected')) DEFAULT 'pending',
  FOREIGN KEY (sender_id) REFERENCES users(user_id),
  FOREIGN KEY (receiver_id) REFERENCES users(user_id)
);


CREATE TABLE IF NOT EXISTS friends (
  user1_id INT NOT NULL,
  user2_id INT NOT NULL,
  FOREIGN KEY (user1_id) REFERENCES users(user_id),
  FOREIGN KEY (user2_id) REFERENCES users(user_id),
  PRIMARY KEY (user1_id, user2_id),
  CHECK(user1_id < user2_id)
);


CREATE TABLE IF NOT EXISTS messages (
  message_id SERIAL PRIMARY KEY,
  sender_id INT NOT NULL,
  receiver_id INT NOT NULL,
  content TEXT NOT NULL,
  time_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_read BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (sender_id) REFERENCES users(user_id),
  FOREIGN KEY (receiver_id) REFERENCES users(user_id)
);


CREATE TABLE IF NOT EXISTS groups (
  group_id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  creator_id INT NOT NULL,
  creator VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  description VARCHAR(140) NOT NULL,
  avatar_link TEXT,
  FOREIGN KEY (creator_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS group_requests (
  group_request_id SERIAL PRIMARY KEY,
  user_id INT NOT NULL,
  group_id INT NOT NULL,
  requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(20) CHECK (status in ('pending', 'accepted', 'rejected')) DEFAULT 'pending',
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (group_id) REFERENCES groups(group_id)
);


CREATE TABLE IF NOT EXISTS groups_to_users (
  group_id INT NOT NULL,
  user_id INT NOT NULL,
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (group_id) REFERENCES groups(group_id),
  PRIMARY KEY (group_id, user_id)
);


CREATE TABLE IF NOT EXISTS posts (
  post_id SERIAL PRIMARY KEY,
  creator_id INT NOT NULL,
  content VARCHAR(200) NOT NULL,
  time_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  image_url TEXT,
  group_id INT NOT NULL,
  FOREIGN KEY (creator_id) REFERENCES users(user_id),
  FOREIGN KEY (group_id) REFERENCES groups(group_id)
);


CREATE TABLE IF NOT EXISTS comments (
  comment_id SERIAL PRIMARY KEY,
  creator_id INT NOT NULL,
  post_id INT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  content VARCHAR(140) NOT NULL,
  FOREIGN KEY (creator_id) REFERENCES users(user_id),
  FOREIGN KEY (post_id) REFERENCES posts(post_id)
);
DELETE FROM users;
DELETE FROM friends;
-- DELETE FROM friend_requests;
INSERT INTO users (username, password, email, name) VALUES ('test', 'scrypt:32768:8:1$RZO6a2PV9y9MBqQq$92335e1e4d6b6edcd57ffb9795494d0a006243c7512d3ca93a7f836209521218fd779abd29ed752aa945de9f4fb029480f8a19b35cc17a9a7ae63dd1376e2e41', 'test@gmail.com', 'test');
INSERT INTO users (username, password, email, name) VALUES ('test2', 'scrypt:32768:8:1$LPF4PTBUFHwU7Iir$05ef383ad88ee5149da21f17ebbba89237272d5ec5db59dbdf08e8cf388d122422ddcf4e04652e81eeded7ecd886d602e8a2ad46c42bebb23d95b6f7f0de8cfc', 'test2@gmail.com', 'test2');
--INSERT INTO friends (user1_id, user2_id) VALUES (1, 2);
-- INSERT INTO friend_requests (sender_id, receiver_id) VALUES (1, 2);
SELECT * FROM users;