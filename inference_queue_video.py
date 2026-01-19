import requests
import os

# Set the API endpoint and headers
API_URL = "http://127.0.0.1:5000/queue_video"
HEADERS = {
    "Content-Type": "application/json"
}


def infer_queue_video(video_path, output_path=None):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    payload = {"video_path": video_path}
    if output_path:
        payload["output"] = output_path

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        print("Request successful!")
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(f"Details: {response.json()}")
        response.raise_for_status()


if __name__ == "__main__":
    VIDEO_PATH = "data/demo_clip3.mp4"
    OUTPUT_PATH = "demo_clip3_output.xlsx"

    try:
        result = infer_queue_video(VIDEO_PATH, OUTPUT_PATH)
        print("Response from server:")
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")
