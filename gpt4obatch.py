import os
import cv2
import json
from openai import OpenAI

# Model and client setup
MODEL = "gpt-4o-2024-08-06"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your_openai_api_key_here"))


def validate_video_path(video_path):
    """Validate if the video file exists and is readable."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.access(video_path, os.R_OK):
        raise PermissionError(f"Cannot read video file: {video_path}")
    return True


def extract_frames(video_path, seconds_per_frame=0.5, max_frames=100):
    """Extract frames from the video at regular intervals."""
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    fps = int(video.get(cv2.CAP_PROP_FPS))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = int(fps * seconds_per_frame)

    extracted_frames = []
    frame_count = 0
    current_frame = 0

    print(f"Extracting frames from video: {video_path}...")
    while current_frame < total_frames and frame_count < max_frames:
        video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        success, frame = video.read()
        if not success:
            break

        # Add the frame to the list
        extracted_frames.append(frame)
        frame_count += 1
        current_frame += frame_interval

    video.release()
    print(f"Extracted {len(extracted_frames)} frames from video.")
    return extracted_frames


def prepare_jsonl_from_frames(frames):
    """Prepare JSONL payload from extracted frames in batches of 10."""
    jsonl_data = ""
    batch_size = 10

    # Split frames into batches of 10
    for batch_idx in range(0, len(frames), batch_size):
        batch_frames = frames[batch_idx:batch_idx + batch_size]

        # Encode each frame in the batch as base64
        encoded_images = []
        for frame in batch_frames:
            _, buffer = cv2.imencode('.jpg', frame)
            base64_image = buffer.tobytes().hex()
            encoded_images.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "low"
                }
            })

        # Create a single JSONL entry for this batch
        jsonl_data += json.dumps({
            "custom_id": f"batch-{batch_idx // batch_size}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a structured robot that outputs results from gambling frames in a strict format."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Find and fill these columns with the correct values from the game HUD and not from the game: "
                                        "Game name, Credit, Bet, Win, Total Win, Free spins left, Auto spins and Feature (boolean). "
                                        "Differentiate between free spins left and auto spins. Feature=True means the bonus feature "
                                        "is active. Usually, the feature comes with free spins left. If Feature=False, it MIGHT have "
                                        "auto spins. Sometimes, synonyms are used instead of the expected words, i.e. balance or coins "
                                        "instead of credit, if you find such a word, extract their value for the 'credit' column. This "
                                        "applies to all columns or for different languages. If something is not present in the image, "
                                        "pass N/A in the field. Include currency in the output. ALWAYS return output from ALL 10 images."
                            },
                            *encoded_images
                        ]
                    }
                ]
            }
        }) + "\n"

    return jsonl_data


def upload_jsonl(jsonl_data, filename):
    """Upload JSONL data as a file to OpenAI."""
    # Save the JSONL data to a temporary file
    with open(filename, "w") as file:
        file.write(jsonl_data)

    # Upload the file
    with open(filename, "rb") as file:
        response = client.files.create(file=file, purpose="batch")

    # Check response
    if "id" not in response:
        raise Exception(f"File upload failed: {response}")
    return response["id"]


def create_batch(input_file_id):
    """Create a batch using the uploaded file ID."""
    response = client.batches.create(
        input_file_id=input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    if "id" not in response:
        raise Exception(f"Batch creation failed: {response}")
    return response


def process_video_batch(video_path, jsonl_filename, seconds_per_frame=0.5, max_frames=100):
    """Main function to process a video and queue a batch."""
    validate_video_path(video_path)
    frames = extract_frames(video_path, seconds_per_frame, max_frames)
    jsonl_data = prepare_jsonl_from_frames(frames)
    input_file_id = upload_jsonl(jsonl_data, jsonl_filename)
    batch_info = create_batch(input_file_id)

    return batch_info
