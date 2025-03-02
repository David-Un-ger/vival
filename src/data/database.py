import os

from psycopg2.pool import ThreadedConnectionPool

from src.data.generate import create_dictionary

pool = ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host="postgres",
    port="5432",
)


def create_table():
    """Creates the dictionary table in the database."""
    conn = pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE dictionary (
                    id SERIAL PRIMARY KEY,
                    word TEXT NOT NULL,
                    meaning TEXT NOT NULL,
                    synonyms TEXT NOT NULL
                )
            """)
            conn.commit()
    finally:
        pool.putconn(conn)


def drop_table(table_name: str):
    """Drops the given table from the database."""
    conn = pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.commit()
    finally:
        pool.putconn(conn)


def get_dictionary(word: str) -> dict:
    """Gets dictionary information for a word from the database.

    If it does not exist, it creates it and puts it into the database."""

    conn = pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM dictionary WHERE word = '{word}'")
            dictionary = cursor.fetchall()
    finally:
        pool.putconn(conn)

    if dictionary:
        return dictionary[0]

    dictionary = create_dictionary(word)
    put_dictionary(word, dictionary["error"], dictionary.get("suggestions", []))
    return dictionary


def put_dictionary(word: str, error: str, suggestions: list):
    """Puts dictionary information for a word into the database."""
    conn = pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO dictionary (word, error, suggestions) VALUES ('{word}', '{error}', '{suggestions}')"
            )
            conn.commit()
    finally:
        pool.putconn(conn)
