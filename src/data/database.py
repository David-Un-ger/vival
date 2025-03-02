import base64
import os
from io import BytesIO

from PIL import Image
from psycopg2.pool import ThreadedConnectionPool

from src.data.generate import generate_dictionary, generate_image
from src.definitions import DICTIONARY_TABLE_NAME, IMAGE_FOLDER

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
            cursor.execute(f"""
                CREATE TABLE {DICTIONARY_TABLE_NAME} (
                    id SERIAL PRIMARY KEY,
                    word TEXT NOT NULL,
                    meaning TEXT NOT NULL,
                    synonyms TEXT NOT NULL,
                    usage TEXT NOT NULL,
                    phonetics TEXT NOT NULL,
                    pronunciation TEXT NOT NULL,
                    image_description TEXT NOT NULL,
                    error TEXT NOT NULL,
                    suggestions TEXT NOT NULL
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
            cursor.execute(f"SELECT * FROM {DICTIONARY_TABLE_NAME} WHERE word = '{word}'")
            dictionary = cursor.fetchall()
    finally:
        pool.putconn(conn)

    if dictionary:
        return dictionary[0]

    dictionary = generate_dictionary(word)
    put_dictionary(word, dictionary["error"], dictionary.get("suggestions", []))
    return dictionary


def put_dictionary(word: str, error: str, suggestions: list):
    """Puts dictionary information for a word into the database."""
    conn = pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {DICTIONARY_TABLE_NAME} (word, error, suggestions) VALUES ('{word}', '{error}', '{suggestions}')"
            )
            conn.commit()
    finally:
        pool.putconn(conn)


def get_image(word: str, image_description: str | None = None) -> str:
    """Gets the image for a word from the database.

    If it does not exist, it creates it and stores it on the drive.

    TODO: handle here if the image is giberish, inappropriate or not a word."""

    image_path = IMAGE_FOLDER / f"{word}.png"
    if not image_path.exists():
        image_response = generate_image(image_description)
        image_base64 = image_response.data[0].b64_json
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        image.save(image_path)
        print(f"Image saved to {image_path}")
    return f"/images/{word}.png"


if __name__ == "__main__":
    create_table()
