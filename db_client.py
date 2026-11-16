import psycopg2

from resources.db_creds import DbCreds


def print_postgres_server_info():
    connection = psycopg2.connect(**DbCreds.get_creds())
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT version(), current_database(), "
                "inet_server_addr(), inet_server_port();"
            )
            version, database, host, port = cursor.fetchone()

        print(f"PostgreSQL server: {version}")
        print(f"Database: {database}")
        print(f"Server address: {host}:{port}")
    finally:
        connection.close()


if __name__ == "__main__":
    print_postgres_server_info()
