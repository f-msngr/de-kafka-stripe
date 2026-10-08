COPY (SELECT * FROM 'data/raw/transactions_all.csv' WHERE CAST(trans_date_trans_time AS TIMESTAMP) < TIMESTAMP '2020-12-12 00:00:00') TO 'data/split/transactions.csv' (HEADER, DELIMITER ',');

COPY (SELECT * EXCLUDE (is_fraud) FROM 'data/raw/transactions_all.csv' WHERE CAST(trans_date_trans_time AS TIMESTAMP) >= TIMESTAMP '2020-12-12 00:00:00') TO 'data/split/feed.csv' (HEADER, DELIMITER ',');

COPY (SELECT trans_num, is_fraud FROM 'data/raw/transactions_all.csv' WHERE CAST(trans_date_trans_time AS TIMESTAMP) >= TIMESTAMP '2020-12-12 00:00:00') TO 'data/split/transactions_status.csv' (HEADER, DELIMITER ',');