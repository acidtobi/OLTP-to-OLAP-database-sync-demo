from faker import Faker
import random
import time
import pymysql
from datetime import datetime

MAX_DELAY_SECONDS = 3

fake = Faker()

conn = pymysql.connect(
    host='mysql-oltp',
    port=8000,
    user='ppro',
    password='ppro_password',
    db='oltp',
    cursorclass=pymysql.cursors.DictCursor
)

print("Row inserter service connected to transactions database")

try:
    with conn.cursor() as cursor:

        while True:

            user_id = fake.random_int(min=1, max=100)
            transaction_timestamp = fake.date_time_between(start_date='-1y', end_date='now')
            transaction_amount = random.uniform(-100.0, 100.0)
            transaction_note = fake.text(max_nb_chars=100)
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            sql = """
                INSERT INTO transactions
                    (user_id,
                     transaction_timestamp,
                     transaction_amount,
                     transaction_note,
                     created_at)
                 VALUES
                     (%s, %s, %s, %s, %s)
            """

            cursor.execute(sql,
                (user_id,
                 transaction_timestamp,
                 transaction_amount,
                 transaction_note,
                 created_at)
            )

            conn.commit()

            cursor.execute('SELECT COUNT(*) FROM transactions')
            num_transactions = cursor.fetchone()['COUNT(*)']
            print("Transactions table now contains %d transactions" % num_transactions)

            ## wait for up to MAX_DELAY_SECONDS until next transaction is inserted
            time.sleep(random.random() * MAX_DELAY_SECONDS)

finally:
    conn.close()
