use olap;

CREATE USER 'ppro'@'%' IDENTIFIED BY 'ppro_password';
GRANT SELECT, INSERT, DELETE, UPDATE ON `olap`.* TO 'ppro'@'%';
FLUSH PRIVILEGES;

CREATE TABLE transactions_delta (
    user_id INT NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_amount FLOAT NOT NULL,
    transaction_note VARCHAR(100),
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE balance (
    user_id INT NOT NULL,
    total_amount FLOAT NOT NULL
);
