import cv2
import pandas as pd
import base64
from openai import OpenAI
import os
from tqdm import tqdm

# Setup OpenAI client
MODEL = "gpt-4o-mini"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", None))

# Path to your video
VIDEO_PATH = "data/demo_clip2.mp4"


def encode_image(image):
    # Encode the frame to base64
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')


def process_frames(frames, timestamps):
    # Encode all frames in base64
    base64_images = [encode_image(frame) for frame in frames]

    # Prepare images as part of the user message payload
    images_payload = []
    for base64_image in base64_images:
        images_payload.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })

    # Make API call to GPT-4o mini with frames
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": "You are a structured robot that outputs results from gambling frames in a strict CSV-like format."},
            {"role": "user", "content": [
                {"type": "text",
                 "text": "Extract the labels 'game name', 'credit', 'bet', 'win', and 'total win' from each frame in the following CSV format:"
                         "'timestamp;game name;credit;bet;win;total win'. "
                         "If data is not available, use 'N/A' in the field. "
                         "Output strictly in CSV format without any extra text."},
                *images_payload
            ]}
        ],
        temperature=0.0,
    )

    # Parse the response to ensure it has a consistent format
    outputs = response.choices[0].message.content.strip().split('\n')
    parsed_results = []

    for output in outputs:
        # Split using semicolon and validate the number of fields
        fields = output.split(';')
        if len(fields) == 6:
            parsed_results.append(fields)
        else:
            # Handle inconsistencies gracefully by filling missing fields with 'N/A'
            while len(fields) < 6:
                fields.append('N/A')
            parsed_results.append(fields)

    # Create list of tuples with timestamp and parsed output data
    result_data = [(timestamps[i], *parsed_results[i][1:]) for i in range(len(timestamps))]

    return result_data


def extract_frames(video_path, seconds_per_frame=0.5, batch_size=10):
    # Capture the video
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_to_skip = int(fps * seconds_per_frame)

    data = []
    current_frame = 0
    batch_frames = []
    batch_timestamps = []

    # Use tqdm for progress bar, based on the number of frames in the video
    with tqdm(total=total_frames, desc="Processing Video") as pbar:
        while current_frame < total_frames - 1:
            video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            success, frame = video.read()
            if not success:
                break

            # Get the timestamp in milliseconds
            timestamp = video.get(cv2.CAP_PROP_POS_MSEC)

            # Add the frame and its timestamp to the batch
            batch_frames.append(frame)
            batch_timestamps.append(timestamp)

            # Update the progress bar
            pbar.update(frames_to_skip)

            # Once the batch is filled, process the frames
            if len(batch_frames) == batch_size:
                batch_results = process_frames(batch_frames, batch_timestamps)
                data.extend(batch_results)
                batch_frames = []
                batch_timestamps = []

            # Skip frames by the defined interval
            current_frame += frames_to_skip

        # If any leftover frames, process them
        if batch_frames:
            batch_results = process_frames(batch_frames, batch_timestamps)
            data.extend(batch_results)

    video.release()
    print("Video processing complete.")
    return data


def process_video(video_path, excel_filename="video_results.xlsx"):
    # Extract frames and process them in batches
    print(f"Starting video processing: {video_path}")
    frame_data = extract_frames(video_path)

    # Convert frame_data to a pandas DataFrame
    df = pd.DataFrame(frame_data, columns=["Timestamp (ms)", "Game Name", "Credit", "Bet", "Win", "Total Win"])

    # Ensure all columns have consistent data types and replace 'N/A' with NaN if needed
    df.replace('N/A', pd.NA, inplace=True)

    # Save DataFrame to Excel
    df.to_excel(excel_filename, index=False)
    print(f"DataFrame saved to {excel_filename}")

    return df


# Process the video and generate the DataFrame
excel_filename = "C:\\Users\\User\\Desktop\\Work\\gpt4oimagecapture\\video_results.xlsx"
df_video_results = process_video(VIDEO_PATH, excel_filename=excel_filename)


# Print the DataFrame
print(df_video_results)
