-- Clear any existing tables
DROP TABLE IF EXISTS spending;
DROP TABLE IF EXISTS income;
DROP TABLE IF EXISTS debt;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS expenses;
DROP TABLE IF EXISTS users;

-- Creating new tables
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY NOT NULL,
    username varchar(25) NOT NULL,
    password char(200) NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE expenses (
    expense_id SERIAL PRIMARY KEY NOT NULL,
    name varchar(100) NOT NULL,
    expected MONEY NOT NULL,
    due_date DATE NOT NULL,
    repeat_type varchar(25) NOT NULL,
    owner varchar(25),
    notes varchar(255),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    unique(name),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE goals (
    goal_id SERIAL PRIMARY KEY NOT NULL,
    name varchar(100) NOT NULL,
    target MONEY NOT NULL,
    amount MONEY NOT NULL,
    target_date DATE,
    owner varchar(50),
    notes varchar(255),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE debt (
    debt_id SERIAL PRIMARY KEY NOT NULL,
    name varchar(100) NOT NULL,
    amount MONEY NOT NULL,
    target_date DATE,
    owner varchar(50),
    notes varchar(255),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE income (
    income_id SERIAL PRIMARY KEY NOT NULL,
    name varchar(100) NOT NULL,
    amount MONEY NOT NULL,
    date DATE NOT NULL,
    type varchar(10) NOT NULL,
    owner varchar(50),
    notes varchar(255),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE spending (
    spending_id SERIAL PRIMARY KEY NOT NULL,
    name varchar(100) NOT NULL,
    amount MONEY NOT NULL,
    date DATE not NULL,
    category varchar(50),
    expense_name varchar(50),
    owner varchar(50),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    notes varchar(255),
    user_id INT NOT NULL,
    goal_id INT,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(goal_id) REFERENCES goals(goal_id),
    FOREIGN KEY(expense_name) REFERENCES expenses(name)
);
