import cv2
import pandas as pd
import time
import json
import base64
from openai import OpenAI
import os
from tqdm import tqdm

# Setup OpenAI client
MODEL = "gpt-4o-2024-08-06"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", None))


def encode_image(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')


def process_frames(frames, timestamps):
    base64_images = [encode_image(frame) for frame in frames]

    images_payload = []
    for base64_image in base64_images:
        images_payload.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}",
                "detail": "low"
            }
        })

    response = client.chat.completions.create(
        model=MODEL,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "game_data",
                "schema": {
                    "type": "object",
                    "properties": {
                        "images": {
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
                    "required": ["images"],
                    "additionalProperties": False
                },
                "strict": True
            }
        },
        messages=[
            {"role": "system",
             "content": "You are a structured robot that outputs results from gambling frames in a strict format."},
            {"role": "user", "content": [
                {"type": "text",
                 "text": "Find and fill these columns with the correct values from the game HUD: "
                         "Game name, Credit, Bet, Win, Total Win, Free spins left, Auto spins and Feature (boolean). "
                         "Differentiate between free spins left and auto spins. Feature=True means the bonus feature "
                         "is active. Usually, the feature comes with free spins left. If Feature=False, it MIGHT have "
                         "auto spins. Sometimes, synonyms are used instead of the expected words, i.e. balance or coins"
                         "instead of credit, if you find such word, extract their value for the 'credit' column. This "
                         "applies for all columns or for different languages. If something is not present in the image,"
                         "pass 'Unknown' in the field. Include currency in the output. ALWAYS return output from ALL 10 images"},
                *images_payload
            ]}
        ],
        temperature=0.0,

    )

    outputs = response.choices[0].message.content.split(';')

    return [(timestamp, output) for timestamp, output in zip(timestamps, outputs)]


def extract_frames(video_path, seconds_per_frame=1, batch_size=10):
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        raise FileNotFoundError(f"Could not open video file: {video_path}")

    fps = round(video.get(cv2.CAP_PROP_FPS))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_to_skip = int(fps * seconds_per_frame)

    current_frame = 0
    batch_frames = []
    batch_timestamps = []
    df = pd.DataFrame()

    print(f"Processing video: {video_path} with {total_frames} frames.")

    while current_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        success, frame = video.read()
        if not success:
            print(f"Failed to read frame at position {current_frame}.")
            break

        timestamp = float(current_frame)/fps
        batch_frames.append(frame)
        batch_timestamps.append(timestamp)

        if len(batch_frames) == batch_size:
            batch_results = process_frames(batch_frames, batch_timestamps)
            current_data = json.loads(batch_results[0][1])
            current_df = pd.DataFrame(current_data["images"])
            df = pd.concat([df, current_df], ignore_index=True)
            batch_frames = []
            batch_timestamps = []

        current_frame += frames_to_skip

    if batch_frames:
        batch_results = process_frames(batch_frames, batch_timestamps)
        current_data = json.loads(batch_results[0][1])
        current_df = pd.DataFrame(current_data["images"])
        df = pd.concat([df, current_df], ignore_index=True)

    video.release()
    print("Video processing complete.")
    return df


def process_video(video_path, excel_filename=None):
    if not excel_filename:
        clip_name = os.path.splitext(os.path.basename(video_path))[0]
        excel_filename = f"output/{clip_name}_output.xlsx"
    else:
        excel_filename = f"output/{excel_filename}"

    df = extract_frames(video_path)
    df.to_excel(excel_filename, index=False)
    print(f"Results saved to: {excel_filename}")
    return df


if __name__ == "__main__":
    VIDEO_PATH = "data/demo_clip3.mp4"
    df_video_results = process_video(VIDEO_PATH, excel_filename="output_results.xlsx")
    print(df_video_results)
