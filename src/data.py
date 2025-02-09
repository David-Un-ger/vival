import base64
import json
from io import BytesIO
from pathlib import Path

from diskcache import Cache
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

cache = Cache(".cache")
load_dotenv()
openai = OpenAI()

system_prompt = """You are an expert in language and are asked to help the user to 
get a better understanding of words. 

The user will provide a word as input and you will help him get a better understanding.


Therefore, you will answer in JSON with the following information.
The keys are "meaning", "synonyms", "usage", "phonetics", "pronunciation", "image_description".

- meaning: provide a short description what a word means. Use simple but clear words
- synonyms: which other words are similar or do mean the same
- usage: 2 short sentences that explain how the word is used
- phonetics: how the word is pronounced as IPA
- pronunciation: similar sounding words
- image_description: a short description of an image that could be shown to the user. This text is later processed by the AI to generate an image.


An example: User input: "embrace"

Output:
{
  "word": "embrace",
  "meaning": "To hug someone or accept something willingly and with enthusiasm.",
  "synonyms": ["hug", "accept", "adopt", "welcome", "support"],
  "usage": [
    "She embraced her friend tightly after not seeing him for years.",
    "He decided to embrace the new changes at work with a positive attitude."
  ],
  "phonetics": "ɛmˈbɹeɪs/",
  "pronunciation": ["empty", "emerge", "bracelet", "race"],
  "image_description": "A person hugging another person. One can see the bracelet on the arm of the person."
}
"""


@cache.memoize()
def get_dictionary(word: str) -> dict:
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": word}]
    print(f"Generating dictionary for {word}")
    model_output = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    reply_str = model_output.choices[0].message.content
    return json.loads(reply_str)


def get_image(word: str, image_description: str) -> str:
    image_path = Path(f"C:\\Scarlett\\llm_engineering\\vival\\dictionary\\assets\\images\\{word}.png")
    if image_path.exists():
        print("Existing image found")
        return f"assets/images/{word}.png"
    print(f"Generating image for {word} with description {image_description}")
    image_response = openai.images.generate(
        model="dall-e-3",
        prompt=image_description,
        size="1024x1024",
        n=1,
        response_format="b64_json",
    )
    image_base64 = image_response.data[0].b64_json
    image_data = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_data))
    image.save(image_path)
    print(f"Image saved to {image_path}")

    return f"assets/images/{word}.png"
