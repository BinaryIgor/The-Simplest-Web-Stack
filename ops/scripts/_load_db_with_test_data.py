import uuid

from psycopg2.extras import execute_batch

from os import environ
from commons import db, crypto

secrets = crypto.decrypted_secrets()

db_host= environ["DB_HOST"]
db_port= environ["DB_PORT"]
db_name = environ["DB_NAME"]
db_user = environ["DB_USER"]


db_conn = db.connection(user=db_user, password=secrets["db-password"], db_name=db_name, 
                        db_host=db_host, db_port=db_port)

cur = db_conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS account (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL          
);""")

batches = environ.get("BATCHES", 100)
batch_size = environ.get("BATCH_SIZE", 1000)

print(f"About to insert {batches} batches, {batch_size} each...")

for i in range(batches):
    print(f"Inserting {i}/{batches} batch...")
    account_idx = i * batch_size
    account_tuples = [(str(uuid.uuid4()), f"name{account_idx + j}", f"email{account_idx + j}@email.com") for j in range(batch_size)]
    execute_batch(cur, "INSERT INTO account (id, name, email) VALUES (%s, %s, %s)", account_tuples)

print()
print(f"{batches * batch_size} accounts inserted!")
