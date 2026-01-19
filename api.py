from flask import Flask, request, jsonify
import os
import cv2
import json
import base64
import uuid
import matplotlib.pyplot as plt

app = Flask(__name__)

OUTPUT_DIR = "output"
INPUT_DATA_FILES_DIR = "input_data_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DATA_FILES_DIR, exist_ok=True)

def validate_video_path(video_path):
    if not os.path.exists(video_path):
        return False, "Video path does not exist."
    if not os.path.isfile(video_path):
        return False, "Provided path is not a valid file."
    if not video_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
        return False, "Unsupported video file format. Only .mp4, .avi, .mkv, .mov are allowed."
    return True, None


@app.route('/generate_images', methods=['POST'])
def generate_images():
    """
    Extract frames from the video, preprocess them, and create JSONL files for the Batch API.
    """
    try:
        data = request.json
        video_path = data.get('video_path')

        if not video_path:
            return jsonify({"error": "Video path is required."}), 400

        is_valid, error = validate_video_path(video_path)
        if not is_valid:
            return jsonify({"error": error}), 400

        task_id = str(uuid.uuid4())
        output_task_dir = os.path.join(OUTPUT_DIR, task_id)
        jsonl_dir = os.path.join(INPUT_DATA_FILES_DIR, task_id)
        os.makedirs(output_task_dir, exist_ok=True)
        os.makedirs(jsonl_dir, exist_ok=True)

        video = cv2.VideoCapture(video_path)
        fps = int(video.get(cv2.CAP_PROP_FPS))
        frame_interval = fps // 2
        success, frame_count, extracted_count = True, 0, 0

        frames = []
        while success:
            success, frame = video.read()
            if frame_count % frame_interval == 0 and success:
                resized_frame = cv2.resize(frame, (512, 512), interpolation=cv2.INTER_AREA)
                frame_path = os.path.join(output_task_dir, f"frame_{extracted_count}.jpg")
                cv2.imwrite(frame_path, resized_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])  # Compress JPEG
                frames.append(frame_path)
                extracted_count += 1
            frame_count += 1
        video.release()

        max_batch_size = 50000
        current_batch_size = 0
        batch_index = 1
        tasks = []
        batch_files = []

        for i, frame_path in enumerate(frames):
            with open(frame_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

            tasks.append({
                "custom_id": f"task-{i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",
                    "temperature": 0,
                    "max_tokens": 500,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a structured robot that processes gambling game images and outputs results in a strict format."
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extract the following fields from the images: Game name, Credit, Bet, Win, Total Win, Free spins left, Auto spins, Feature (boolean). Use the strict JSON schema below to format the output. If any value is not present, return N/A."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}", "detail": "low"}}
                            ]
                        }
                    ],
                    "response_format": {
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
                }
            })

            current_batch_size += len(img_base64.encode('utf-8')) + len(json.dumps(tasks[-1]).encode('utf-8'))

            if current_batch_size >= max_batch_size or i == len(frames) - 1:
                batch_file = os.path.join(jsonl_dir, f"batch_{batch_index}.jsonl")
                with open(batch_file, 'w') as file:
                    for task in tasks:
                        file.write(json.dumps(task) + '\n')
                batch_files.append(batch_file)

                tasks = []
                current_batch_size = 0
                batch_index += 1

        return jsonify({
            "message": "Frames and JSONL files generated successfully.",
            "task_id": task_id,
            "output_directory": output_task_dir,
            "jsonl_files": batch_files,
            "frame_count": extracted_count
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
