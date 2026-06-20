from flask import Flask, request, Response, jsonify
from functools import wraps
import os
import uuid
import io
from PIL import Image

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
filename = "/home/kkarousel/cover.png"
env_var_api_key = "API-KEY"

# Load or create API key
try:
    from keys import api_keys
except Exception as e:
    print("no secrets found. Generating new api key.", e)
    key = os.environ.get(env_var_api_key, "")
    if key == "":
        key = str(uuid.uuid4())
    api_keys = [key]
    with open("/home/kkarousel/keys.py", "w") as f:
        f.write(f"api_keys = ['{key}']")

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if api_key not in api_keys:
            return jsonify({"error": "invalid api key"}), 401
        return f(*args, **kwargs)
    return decorated

# Routes

@app.route("/upload", methods=["POST"])
@require_api_key
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "no file provided"}), 400

    file = request.files["file"]

    if not allowed_file(file.filename):
        return jsonify({"error": "invalid file extension"}), 403

    content = file.read()
    image = Image.open(io.BytesIO(content)).convert('L')
    image.save(filename)

    return jsonify(True)


@app.route("/download", methods=["GET"])
@require_api_key
def download_image():
    try:
        with open(filename, "rb") as f:
            return Response(f.read(), mimetype="image/png")
    except FileNotFoundError:
        return jsonify({"error": "file not found"}), 404


# Local dev only
if __name__ == "__main__":
    app.run(debug=True)