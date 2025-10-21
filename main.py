from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    image_bytes = request.files["file"].read()
    HUGGINGFACE_API = "https://api-inference.huggingface.co/models/umm-maybe/AI-image-detector"

    try:
        response = requests.post(HUGGINGFACE_API, data=image_bytes, timeout=60)
        content_type = response.headers.get("content-type", "")
        data = response.json() if "application/json" in content_type else {}

        if response.status_code != 200:
            return jsonify({"error": f"Model error {response.status_code}", "details": data}), 502

        label = data[0]["label"] if isinstance(data, list) and data else "Unknown"
        score = data[0]["score"] if isinstance(data, list) and data else 0

        verdict = (
            "✅ Real photo" if "real" in label.lower() and score > 0.6
            else "⚠️ AI-generated"
        )

        return jsonify({"verdict": verdict, "confidence": round(score, 3), "raw": data})

    except Exception as e:
        return jsonify({"error": f"Server failure: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)