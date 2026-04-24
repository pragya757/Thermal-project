import os
import uuid
from flask import Flask, request, jsonify, render_template, Response
from werkzeug.utils import secure_filename
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from model import analyze_thermal_image

app = Flask(__name__)

# -----------------------------
# Prometheus Metric
# -----------------------------
REQUEST_COUNT = Counter('request_count_total', 'Total number of requests')

# -----------------------------
# Upload Config
# -----------------------------
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def index():
    REQUEST_COUNT.inc()
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    REQUEST_COUNT.inc()

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded. Use key 'image'."}), 400

    file = request.files["image"]

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or missing file."}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{uuid.uuid4().hex}.{ext}")

    try:
        file.save(save_path)
        result = analyze_thermal_image(save_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)

    return jsonify(result), 200


# -----------------------------
# Metrics Endpoint (VERY IMPORTANT)
# -----------------------------
@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)