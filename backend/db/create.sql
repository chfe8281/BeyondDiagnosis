
CREATE TABLE IF NOT EXISTS users (
  user_id SERIAL PRIMARY KEY NOT NULL,
  username VARCHAR(50) NOT NULL,
  password VARCHAR(225) NOT NULL,
  email VARCHAR(50) NOT NULL,
  name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS profiles (
  user_id INT PRIMARY KEY NOT NULL,
  bio VARCHAR(200),
  avatar_url TEXT,
  location VARCHAR(50),
  conditions TEXT[],
  interests TEXT[],
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
  content VARCHAR(200) NOT NULL,
  time_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_read BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (sender_id) REFERENCES users(user_id),
  FOREIGN KEY (receiver_id) REFERENCES users(user_id)
);


CREATE TABLE IF NOT EXISTS groups (
  group_id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  creator_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  description VARCHAR(140) NOT NULL,
  FOREIGN KEY (creator_id) REFERENCES users(user_id)
);


CREATE TABLE IF NOT EXISTS groups_to_users (
  group_id INT NOT NULL,
  user_id INT NOT NULL,
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (group_id) REFERENCES groups(group_id)
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
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  content VARCHAR(140) NOT NULL,
  FOREIGN KEY (creator_id) REFERENCES users(user_id),
  FOREIGN KEY (post_id) REFERENCES posts(post_id)
);

