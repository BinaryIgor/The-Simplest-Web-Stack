import time

from os import environ
from commons import db, crypto

secrets = crypto.decrypted_secrets()

ROOT_USER = "postgres"
INITIAL_ROOT_PASSWORD = "postgres"

root_password = secrets["db-root-password"]

db_host=environ["DB_HOST"]
db_port=environ["DB_PORT"]
db_name = environ["DB_NAME"]
db_user = environ["DB_USER"]

connect_trials = 5

for i in range(connect_trials):
    try:
        try:
            conn = db.root_connection(ROOT_USER, INITIAL_ROOT_PASSWORD, db_host=db_host, db_port=db_port)
        except Exception:
            print("Failed to use initial root password, will use next one instead")
            conn = db.root_connection(ROOT_USER, root_password)
            break
    except Exception:
        should_retry = (i + 1) < connect_trials
        if should_retry:
            print("Can't connect to db, will retry in 1s")
            time.sleep(1)
        else:
            raise Exception(f"Failed to connect to db in {connect_trials} trials")

cur = conn.cursor()

db.create_db_if_does_not_exist(cur, db_name)
db.create_user_if_does_not_exist(cur, db_user, secrets["db-password"], db_name, privileges='ALL')

# db_reader_user = f'{db_user}_reader'
# db.create_user_if_does_not_exist(cur, db_reader_user, secrets["db-reader-password"], db_name)

# print(f"{db_user} and {db_reader_user} users for {db_name} created, rotating root password...")

print(f"{db_user} user for {db_name} created, rotating root password...")

root_password = secrets['db-root-password']
db.alter_user_password(cur, ROOT_USER, root_password)

print("Granting db rights...")
db_conn = db.root_connection(ROOT_USER, root_password, db_name=db_name, db_host=db_host, db_port=db_port)

cur = db_conn.cursor()

db.grant_schema_privileges(cur, "public", db_user, privileges="ALL")
# db.grant_read_privileges(cur, db_reader_user, db_name)

print("Db initialized")
