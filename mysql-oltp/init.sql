use oltp;

CREATE USER 'ppro'@'%' IDENTIFIED BY 'ppro_password';
GRANT SELECT, INSERT ON `oltp`.* TO 'ppro'@'%';
FLUSH PRIVILEGES;

CREATE TABLE transactions (
    user_id INT NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_amount FLOAT NOT NULL,
    transaction_note VARCHAR(100),
    created_at TIMESTAMP NOT NULL
);
