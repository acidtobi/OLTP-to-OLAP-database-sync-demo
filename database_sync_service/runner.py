import time
import pymysql
from datetime import datetime

# number of rows which will be fetched per iteration
BLOCKSIZE = 1000

source_conn = pymysql.connect(
    host='mysql-oltp',
    port=8000,
    user='ppro',
    password='ppro_password',
    db='oltp',
    cursorclass=pymysql.cursors.SSCursor,
    autocommit=True
)

print("Sync service connected to source database")

target_conn = pymysql.connect(
    host='mysql-olap',
    port=9000,
    user='ppro',
    password='ppro_password',
    db='olap',
    cursorclass=pymysql.cursors.DictCursor
)

print("Sync service connected to target database")

# clear existing tables
with target_conn.cursor() as target_cursor:
    target_cursor.execute('DELETE FROM transactions_delta')
    target_cursor.execute('DELETE FROM balance')
    target_conn.commit()

def sync_transactions(min_timestamp=datetime.min):
    with (
        source_conn.cursor() as source_cursor,
        target_conn.cursor() as target_cursor
    ):
        total_transactions_synced = 0
        latest_timestamp = min_timestamp

        min_timestamp_str = min_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        source_cursor.execute("SELECT * FROM transactions WHERE created_at > '%s' ORDER BY created_at" % min_timestamp_str)

        while True:
            source_transactions = source_cursor.fetchmany(BLOCKSIZE)
            total_transactions_synced += len(source_transactions)

            if len(source_transactions) == 0:
                break

            latest_transaction = source_transactions[-1]
            user_id, transaction_timestamp, transaction_amount, transaction_note, created_at = latest_transaction
            latest_timestamp = created_at

            sql = """
                INSERT INTO transactions_delta
                    (user_id,
                     transaction_timestamp,
                     transaction_amount,
                     transaction_note,
                     created_at)
                 VALUES
                     (%s, %s, %s, %s, %s)
            """

            target_cursor.executemany(sql, source_transactions)
            target_conn.commit()

    source_cursor.close()
    target_cursor.close()

    print("Synced %d transactions from OLTP database" % total_transactions_synced)

    return latest_timestamp

# initial load without minimum created timestamp (loads all existing transactions)
watermark_timestamp = sync_transactions()

while True:

    with target_conn.cursor() as target_cursor:

        # update balance table for existing users
        sql = """
            UPDATE balance
            JOIN (
                SELECT
                    user_id,
                    SUM(transaction_amount) AS total_amount
                FROM
                    transactions_delta
                GROUP BY
                    user_id
            ) transactions ON balance.user_id = transactions.user_id
            SET
                balance.total_amount = balance.total_amount + transactions.total_amount;
        """

        target_cursor.execute(sql)
        target_conn.commit()

        # insert rows into balance table for new users
        sql = """
            INSERT INTO balance (user_id, total_amount)
            SELECT
                transactions.user_id,
                transactions.total_amount
            FROM (
                SELECT
                    user_id,
                    SUM(transaction_amount) AS total_amount
                FROM
                    transactions_delta
                GROUP BY
                    user_id
            ) transactions
            LEFT JOIN balance ON transactions.user_id = balance.user_id
            WHERE balance.user_id IS NULL;          
        """

        target_cursor.execute(sql)
        target_conn.commit()

        # delete transactions delta
        target_cursor.execute("DELETE from transactions_delta")
        target_conn.commit()

    # wait for 60 seconds
    time.sleep(60)

    watermark_timestamp = sync_transactions(watermark_timestamp)



