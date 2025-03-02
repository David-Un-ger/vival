import base64
import json
import os
from io import BytesIO

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from openai.types import ImagesResponse
from PIL import Image

from src.data.prompts import dictionary_system_prompt
from src.definitions import IMAGE_FOLDER

load_dotenv()
openai_client = OpenAI()
nebius_client = OpenAI(base_url="https://api.studio.nebius.com/v1/", api_key=os.environ.get("NEBIUS_API_KEY"))


def generate_dictionary(word: str) -> dict:
    messages = [{"role": "system", "content": dictionary_system_prompt}, {"role": "user", "content": word}]
    print(f"Generating dictionary for {word}")
    try:
        model_output = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

    except RateLimitError:
        return {"word": word, "error": "OpenAI rate limit reached"}
    reply_str = model_output.choices[0].message.content
    return json.loads(reply_str)


def generate_image(word: str, image_description: str, generator: str = "nebius") -> str:
    image_path = IMAGE_FOLDER / f"{word}.png"
    if image_path.exists():
        print("Existing image found")
        return f"/images/{word}.png"
    print(f"Generating image for {word} with description {image_description}")

    if generator == "dalle":
        image_response = generate_image_dalle(image_description)
    elif generator == "nebius":
        image_response = generate_image_nebius(image_description)
    else:
        raise ValueError(f"Unknown generator {generator}")

    image_base64 = image_response.data[0].b64_json
    image_data = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_data))
    image.save(image_path)
    print(f"Image saved to {image_path}")
    return f"/images/{word}.png"


def generate_image_dalle(image_description: str) -> ImagesResponse:
    return openai_client.images.generate(
        model="dall-e-3",
        prompt=image_description,
        size="1024x1024",
        n=1,
        response_format="b64_json",
    )


def generate_image_nebius(image_description: str) -> ImagesResponse:
    return nebius_client.images.generate(
        model="black-forest-labs/flux-schnell",
        response_format="b64_json",
        extra_body={
            "response_extension": "webp",
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 4,
            "negative_prompt": "",
            "seed": -1,
        },
        prompt=image_description,
    )
