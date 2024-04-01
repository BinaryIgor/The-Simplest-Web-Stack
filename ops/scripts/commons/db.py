import psycopg2

from . import meta, crypto

def root_connection(root_user=None, root_password=None, db_name=None, db_host=None, db_port=None):
    if root_user is None:
        root_user = "postgres"

    if root_password is None:
        root_password = crypto.decrypted_secrets("db-root-password")

    conn = psycopg2.connect(host=db_host,
                            port=db_port,
                            dbname=db_name if db_name else "postgres",
                            user=root_user,
                            password=root_password,
                            connect_timeout=3)

    conn.autocommit = True

    return conn


def create_db_if_does_not_exist(cursor, db):
    print(f"Creating {db} db...")

    cursor.execute(f"SELECT * FROM pg_database WHERE datname='{db}'")

    res = cursor.fetchone()
    if res:
        print(f"{db} already exists, skipping")
    else:
        cursor.execute(f'CREATE DATABASE "{db}"')


def create_user_if_does_not_exist(cursor, user, password, db, privileges=None, conn_limit=None):
    print(f"Creating {user} user...")

    cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname='{user}'")

    res = cursor.fetchone()
    if res:
        print(f"{user} user already exists, skipping")
    else:
        cursor.execute(f'CREATE USER "{user}" WITH PASSWORD \'{password}\'')

    cursor.execute(f'GRANT CONNECT ON DATABASE "{db}" TO "{user}"')

    if privileges:
        print(f"Granting {privileges} privileges on {db} db to {user}")
        cursor.execute(f'GRANT {privileges} ON DATABASE "{db}" TO "{user}"')

    if conn_limit:
        cursor.execute(f'ALTER USER "{user}" WITH CONNECTION LIMIT {conn_limit}')


def grant_read_privileges(cursor, user, db, schemas=None):
    if schemas is None:
        schemas = ['public']
    elif schemas == 'all':
        cursor.execute("""
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name NOT like 'pg_%';
        """)
        schemas = [r[0] for r in cursor.fetchall()]

    cursor.execute(f'GRANT CONNECT ON DATABASE "{db}" TO "{user}"')

    for s in schemas:
        print(f"Granting read privileges to {user} on schema {s}")
        try:
            grant_schema_privileges(cursor, s, user)
            cursor.execute(f"""
            GRANT SELECT ON ALL TABLES IN SCHEMA "{s}" TO "{user}";
            """)
        except Exception:
            print(f"Failed to grant permissions on {s} schema for {user}")


def grant_schema_privileges(cursor, schema, user, privileges=None):
    cursor.execute(f'GRANT USAGE ON SCHEMA "{schema}" TO "{user}"')

    if privileges:
        print(f"Granting {privileges} privileges on {schema} to {user}")
        if privileges == "ALL":
            cursor.execute(f'GRANT ALL ON  schema "{schema}" TO "{user}"')
        else:
            cursor.execute(f'GRANT {privileges} ON ALL TABLES IN SCHEMA "{schema}" TO "{user}"')
            cursor.execute(f'GRANT {privileges} ON ALL SEQUENCES IN SCHEMA "{schema}" TO "{user}"')


def alter_user_password(cursor, user, password):
    cursor.execute(f"ALTER USER {user} WITH PASSWORD '{password}'")
