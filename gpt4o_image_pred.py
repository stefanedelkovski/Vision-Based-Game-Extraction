from openai import OpenAI
import os
from IPython.display import Image, display, Audio, Markdown
import base64

MODEL = "gpt-4o-2024-08-06"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", None))

IMAGE_PATH = "data/proba15.png"


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


base64_image = encode_image(IMAGE_PATH)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system",
         "content": "You are a structured robot that outputs results from gambling frames in a strict format."},
        {"role": "user", "content": [
            {"type": "text",
             "text": "Find the following things in the images: Game name | Credit | Bet | Win | Total Win | Free spins left | Auto spins | Feature (boolean). Follow this exact structure and give me pd.Series output, these being the column names. Differentiate between free spins left and auto spins. Feature means the bonus feature if he's playing it in the game. Usually, the feature comes with free spins left. So basically, if there's Feature - True, it should have free spins left (usually, depends on the game). If there's Feature - False, it MIGHT have auto spins. You should be able to determine which one is present. If something is not present in the image, just pass N/A in the field. "},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{base64_image}",
                "detail": "low"}
             }
        ]}
    ],
    temperature=0.0,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "game_data",
            "schema": {
                "type": "object",
                "properties": {
                    "Game name": {"type": "string"},
                    "Credit": {"type": "string"},
                    "Bet": {"type": "string"},
                    "Win": {"type": "string"},
                    "Total Win": {"type": "string"},
                    "Free spins left": {"type": "string"},
                    "Auto spins": {"type": "string"},
                    "Feature": {"type": "boolean"}
                },
                "required": [
                    "Game name",
                    "Credit",
                    "Bet",
                    "Win",
                    "Total Win",
                    "Free spins left",
                    "Auto spins",
                    "Feature"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }
)

# Print the response content
print(response.choices[0].message.content)

# Extract and print token usage
usage = response.usage.total_tokens
print(f'Total tokens: {usage}')
