from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
import os
import base64

MODEL = "gpt-4o-2024-08-06"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", None))


class ImageResult(BaseModel):
    game_name: str = Field(..., alias="Game name")
    credit: str = Field(..., alias="Credit or Balance")
    bet: str
    win: str
    total_win: str = Field(..., alias="Total Win")
    free_spins_left: str
    auto_spins: str
    feature: bool


class GameData(BaseModel):
    images: List[ImageResult]


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Paths to images
IMAGE_PATHS = ["data/proba2.png", "data/proba3.png", "data/proba4.png", "data/proba5.png", "data/proba6.png"]
base64_images = [encode_image(image_path) for image_path in IMAGE_PATHS]

completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system",
         "content": "You are a structured robot that outputs results from gambling frames in a strict format."},
        {
            "role": "user",
            "content": [
                {"type": "text",
                 "text": "Find the following things in the images: Game name | Credit | Bet | Win | Total Win | Free spins left | Auto spins | Feature (boolean). Differentiate between free spins left and auto spins. Feature means the bonus feature if he's playing it in the game. Usually, the feature comes with free spins left. So basically, if there's Feature - True, it should have free spins left (usually, depends on the game). If there's Feature - False, it MIGHT have auto spins. You should be able to determine which one is present. If something is not present in the image, just pass N/A in the field."},
                *[
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img}",
                            "detail": "low"
                        }
                    }
                    for img in base64_images
                ]
            ],
        }
    ],
    response_format=GameData  # Use the schema here
)

# Parse the response
response = completion.choices[0].message.parsed

# Output the parsed response
print(response)

# Print individual results
for image_result in response.images:
    print(image_result)

# Extract and print token usage
tokens = completion.usage.total_tokens
print(f"Total tokens: {tokens}")


# Estimated cost function
def tokens_to_dollars(total_tokens, rate_per_1000=0.00125):
    return (total_tokens / 1000) * rate_per_1000


cost = tokens_to_dollars(tokens)
print(f"Estimated Cost in dollars: ${cost:.4f}")
