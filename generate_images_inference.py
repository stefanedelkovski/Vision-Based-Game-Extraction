import os
import requests
import json

# Define the API endpoint for 'generate_images'
API_URL = "http://127.0.0.1:5000/generate_images"

# Relative path to the video (adjust as necessary)
VIDEO_NAME = "demo_clip3.mp4"


def get_absolute_video_path(video_name):
    """
    Constructs the absolute path to the video file.
    """
    # Get the absolute path of the current script's directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to the video
    video_path = os.path.join(project_dir, "data", video_name)
    return video_path


def call_generate_images(video_name):
    """
    Calls the 'generate_images' endpoint with the given video path.
    """
    try:
        # Get the absolute path of the video
        video_path = get_absolute_video_path(video_name)

        # Verify if the file exists
        if not os.path.exists(video_path):
            print(f"Error: Video file does not exist at {video_path}")
            return

        # Prepare the payload
        payload = {"video_path": video_path}

        # Send a POST request to the API
        response = requests.post(API_URL, json=payload)

        # Check the response status
        if response.status_code == 200:
            data = response.json()
            print("Success! Frames and JSONL file generated:")
            print(json.dumps(data, indent=4))
        else:
            print("Error! Status Code:", response.status_code)
            print("Response:", response.json())
    except Exception as e:
        print("An error occurred while calling the API:", str(e))


# Run the function
if __name__ == "__main__":
    call_generate_images(VIDEO_NAME)
