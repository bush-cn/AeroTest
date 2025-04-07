import json
import re
from config import global_config

from flask import Flask, request, Response, send_from_directory, jsonify
import subprocess
import os

app = Flask(__name__, static_folder="dist", static_url_path="/")
CONFIG_FILE = "config.py"


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)


@app.route("/run", methods=["POST"])
def run_api():
    data = request.get_json()
    function_name = data.get("function_name")
    file_name = data.get("file_name")
    reference = data.get("reference", False)

    if not function_name or not file_name:
        return jsonify({"error": "Missing required parameters"}), 400

    def generate():
        process = subprocess.Popen(
            ["python", "run.py", function_name, file_name] + (["--reference"] if reference else []),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in process.stdout:
            yield f"data: {line.rstrip()}\n\n"
        process.wait()
        yield "event: done\ndata: done\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/config", methods=["POST"])
def update_config():
    config_updates = request.get_json()
    if not isinstance(config_updates, dict):
        return jsonify({"error": "Invalid JSON format"}), 400

    if not os.path.exists(CONFIG_FILE):
        return jsonify({"error": "config.py not found"}), 404

    global_config.update(config_updates)
    content = f"global_config = {json.dumps(global_config, indent=4)}\n"

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    return jsonify({"status": "success", "updated": config_updates})


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
