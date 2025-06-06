use sql12771023;
select * from users;
select * from work_time;
select * from app_usage;
select* from screenshots;
ALTER TABLE users CHANGE is_active status VARCHAR(10) DEFAULT NULL;

CREATE TABLE screenshots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    screenshot_path VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    INDEX idx_user_id (user_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;



CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(36) DEFAULT NULL,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_no VARCHAR(20) DEFAULT NULL,
    user_password VARCHAR(255) NOT NULL,
    is_active VARCHAR(10) DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE (username),
    UNIQUE (email),
    UNIQUE (user_id)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE work_time (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36),
    date DATE,
    login_time TIME,
    break_time TIME,
    screen_time TIME,
    logout_time TIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE app_usage (
  id INT NOT NULL AUTO_INCREMENT,
  user_id VARCHAR(36) DEFAULT NULL,
  app_name VARCHAR(255) DEFAULT NULL,
  url VARCHAR(255) DEFAULT NULL,
  duration TIME DEFAULT NULL,
  date DATE DEFAULT NULL,
  PRIMARY KEY (id),
  KEY user_id (user_id),
  CONSTRAINT app_usage_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (user_id)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;