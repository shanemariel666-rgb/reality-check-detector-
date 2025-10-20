from flask import Flask, request, jsonify, render_template_string
import requests, os

app = Flask(__name__)

HIVE_API_KEY = os.getenv("HIVE_API_KEY", "YOUR_HIVE_API_KEY_HERE")

@app.route('/')
def home():
    try:
        with open('index.html', 'r') as f:
            return render_template_string(f.read())
    except Exception as e:
        return f"<h1>Error loading homepage</h1><p>{str(e)}</p>"

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    files = {'media': (file.filename, file.stream, file.mimetype)}
    headers = {"Authorization": f"Token {HIVE_API_KEY}"}

    # 1️⃣ Try Hive AI
    try:
        response = requests.post(
            "https://api.thehive.ai/api/v2/task/sync",
            headers=headers,
            files=files,
            timeout=45
        )
        data = response.json()
        if "output" in data:
            return jsonify({"source": "hive", "result": data})
    except Exception as e:
        print("Hive failed:", e)

    # 2️⃣ Fallback to HuggingFace (works for testing)
    try:
        # Reset the file pointer
        file.stream.seek(0)
        files = {"file": (file.filename, file.stream, file.mimetype)}

        hf_response = requests.post(
            "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32",
            headers={"Authorization": "Bearer hf_FtFpsceYxExampleKey"},  # You can use a free one from HuggingFace
            files=files,
            timeout=45
        )

        hf_data = hf_response.json()
        return jsonify({"source": "huggingface", "result": hf_data})
    except Exception as e:
        return jsonify({"error": f"Both detectors failed: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)