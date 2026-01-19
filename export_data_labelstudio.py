import requests

LABEL_STUDIO_URL = "<labelstudiourl>"
API_KEY = "<labelstudiokey>"
PROJECT_ID = 1
EXPORT_TYPE = "YOLO"

# API endpoint for export
export_url = f"{LABEL_STUDIO_URL}/api/projects/{PROJECT_ID}/export?exportType={EXPORT_TYPE}"

# Headers with API key
headers = {"Authorization": f"Token {API_KEY}"}

# Export data
response = requests.get(export_url, headers=headers, stream=True)

if response.status_code == 200:
    with open("exported_data.zip", "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
    print("Export successful! Data saved to exported_data.zip.")
else:
    print(f"Export failed: {response.status_code} - {response.text}")
