from pathlib import Path

COLOR = "teal.8"  # deprecated
ROOT_PATH = Path(__file__).parent.parent
IMAGE_FOLDER = ROOT_PATH / "assets" / "images"
IMAGE_FOLDER.mkdir(parents=True, exist_ok=True)
DICTIONARY_TABLE_NAME = "dictionary_v1_2"
