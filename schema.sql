-- Clear any existing tables
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS expenses;

-- Creating new tables
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username varchar(25) NOT NULL PRIMARY KEY,
    password char(64) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES goals(user_id),
    FOREIGN KEY(user_id) REFERENCES expenses(user_id)
);

CREATE TABLE expenses (
    expense_id INTEGER PRIMARY KEY,
    name varchar(100) NOT NULL,
    amount MONEY NOT NULL,
    date DATE not NULL,
    category varchar(50),
    type varchar(10) NOT NULL,
    owner varchar(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    goal_id INT,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(goal_id) REFERENCES goals(goal_id)
);

CREATE TABLE goals (
    goal_id INTEGER PRIMARY KEY,
    name varchar(100) NOT NULL,
    amount MONEY NOT NULL,
    target_date DATE,
    type varchar(10) NOT NULL,
    owner varchar(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);