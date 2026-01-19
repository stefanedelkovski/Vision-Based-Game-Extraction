from openai import OpenAI
import os
from IPython.display import Image, display, Audio, Markdown
import base64

MODEL = "gpt-4o-2024-08-06"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", None))

# IMAGE_PATHS = ["data/proba11.jpg", "data/proba12.jpg"]  # Add your image paths here

# Full paths of images
IMAGE_PATHS = [
    os.path.abspath("data/proba11.jpg"),
    os.path.abspath("data/proba12.png"),
    os.path.abspath("data/proba14.png"),
    os.path.abspath("data/proba15.png")
]


def encode_image(image_path):
    """Encode an image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Encode images
encoded_images = [
    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(path)}", "detail": "low"}}
    for path in IMAGE_PATHS]

# Prepare structured messages
messages = [
    {"role": "system",
     "content": "You are a structured robot that outputs results from gambling frames in a strict format."},
    {"role": "user", "content": [
                                    {"type": "text",
                                     "text": "Find the following details in the images: Game name | Credit | Bet | Win | Total Win | Free spins left | Auto spins | Feature (boolean). Follow this exact structure and provide the output as a list of dictionaries, each corresponding to an image. If a detail is not present in an image, use 'N/A' for that field."}
                                ] + encoded_images}
]
# Define the response schema for multiple image outputs
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "game_data_response",
        "schema": {
            "type": "object",
            "properties": {
                "game_data_list": {
                    "type": "array",
                    "items": {
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
                    }
                }
            },
            "required": ["game_data_list"],
            "additionalProperties": False
        },
        "strict": True
    }
}


# Send the request to the OpenAI API
response = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=messages,
    temperature=0.0,
    response_format=response_format
)

# Print the response content
print(response.choices[0].message.content)

# Extract and print token usage
usage = response.usage.total_tokens
print(f'Total tokens: {usage}')
