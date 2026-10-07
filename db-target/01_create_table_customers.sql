CREATE SCHEMA IF NOT EXISTS target;
CREATE TABLE target.customers (
    id INTEGER PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255)
);