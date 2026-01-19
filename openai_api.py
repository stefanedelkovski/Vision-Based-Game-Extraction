from flask import Flask, request, jsonify
from openai import OpenAI
import os
from gpt4ovideo import process_video
from gpt4obatch import process_video_batch


MODEL = "gpt-4o-2024-08-06"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", None))

app = Flask(__name__)


@app.route('/queue_video', methods=['POST'])
def queue_video():
    try:
        data = request.json
        video_path = data.get('video_path')
        if not video_path or not os.path.exists(video_path):
            return jsonify({"error": "Invalid or missing 'video_path' parameter"}), 400

        output = data.get('output')
        if not output:
            clip_name = os.path.splitext(os.path.basename(video_path))[0]
            output = f"{clip_name}_output.xlsx"

        results_df = process_video(video_path, excel_filename=output)
        results_json = results_df.to_dict(orient="records")
        return jsonify({"message": "Video processed successfully", "results": results_json, "output_file": output}), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@app.route('/queue_video_batch', methods=['POST'])
def queue_video_batch():
    try:
        # Parse the request data
        data = request.json
        video_path = data.get("video_path")
        if not video_path:
            return jsonify({"error": "Missing video_path parameter"}), 400

        # Generate a unique JSONL filename
        jsonl_filename = f"{os.path.splitext(os.path.basename(video_path))[0]}_batch.jsonl"

        # Process the video and queue the batch
        batch_info = process_video_batch(
            video_path=video_path,
            jsonl_filename=jsonl_filename,
            seconds_per_frame=0.5,
            max_frames=100
        )

        return jsonify({
            "message": "Batch created successfully",
            "batch_id": batch_info["id"],
            "status": batch_info["status"],
            "input_file_id": batch_info["input_file_id"]
        }), 200

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
