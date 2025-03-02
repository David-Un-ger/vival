import base64
import os
from io import BytesIO

from PIL import Image
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.data.generate import generate_dictionary, generate_image
from src.definitions import DICTIONARY_TABLE_NAME, IMAGE_FOLDER

DATABASE_URL = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@postgres_db:5432/{os.environ['POSTGRES_DB']}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Dictionary(Base):
    __tablename__ = DICTIONARY_TABLE_NAME

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, unique=True, nullable=False)
    meaning = Column(Text)
    synonyms = Column(Text)
    usage = Column(Text)
    phonetics = Column(String)
    pronunciation = Column(Text)
    image_description = Column(Text)
    error = Column(Text)
    suggestions = Column(Text)


def create_table():
    """Creates the dictionary table in the database."""
    Base.metadata.create_all(engine)


def drop_table(table_name: str):
    """Drops the given table from the database."""
    Dictionary.__table__.drop(engine)


def get_dictionary(word: str) -> dict:
    """Gets dictionary information for a word from the database.

    If it does not exist, it creates it and puts it into the database."""

    session = SessionLocal()
    try:
        entry = session.query(Dictionary).filter_by(word=word).first()
        if entry:
            return {
                "word": entry.word,
                "meaning": entry.meaning,
                "synonyms": entry.synonyms.split(",") if entry.synonyms else [],
                "usage": entry.usage.split("\n") if entry.usage else [],
                "phonetics": entry.phonetics,
                "pronunciation": entry.pronunciation.split(",") if entry.pronunciation else [],
                "image_description": entry.image_description,
                "error": entry.error,
                "suggestions": entry.suggestions.split(",") if entry.suggestions else [],
            }

        # If not found, generate and insert
        dictionary = generate_dictionary(word)
        put_dictionary(word, dictionary)
        return dictionary

    finally:
        session.close()


def put_dictionary(word: str, dictionary: dict):
    """Inserts or updates dictionary information for a word."""
    session = SessionLocal()
    try:
        entry = Dictionary(
            word=word,
            meaning=dictionary.get("meaning", ""),
            synonyms=",".join(dictionary.get("synonyms", [])),
            usage="\n".join(dictionary.get("usage", [])),
            phonetics=dictionary.get("phonetics", ""),
            pronunciation=",".join(dictionary.get("pronunciation", [])),
            image_description=dictionary.get("image_description", ""),
            error=dictionary.get("error", ""),
            suggestions=",".join(dictionary.get("suggestions", [])),
        )
        session.merge(entry)  # Upserts the entry
        session.commit()
    finally:
        session.close()


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
