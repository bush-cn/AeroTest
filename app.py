import json
import re
import sys

from config import global_config
from utils.data_processor import load_json

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
    reference = data.get("reference", "").lower() == 'true'

    if not function_name or not file_name:
        return jsonify({"error": "Missing required parameters"}), 400

    def generate():
        # 使用父进程的Python解释器路径（自动识别虚拟环境）
        python_exec = sys.executable
        # 显式传递父进程的工作目录和环境变量
        process = subprocess.Popen(
            [python_exec, "run.py", function_name, file_name] + (["--reference"] if reference else []),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,
            cwd=os.getcwd(),  # 显式继承父进程工作目录
            env=os.environ.copy(),  # 显式继承父进程环境变量
            encoding="utf-8",  # 强制使用 UTF-8
            errors="replace"    # 替换无法解码的字符为占位符
        )
        for line in process.stdout:
            yield f"data: {line.rstrip()}\n\n"
        process.wait()
        yield "event: done\ndata: done\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/config", methods=["POST"])
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


@app.route("/config", methods=["GET"])
def get_config():
    if not os.path.exists(CONFIG_FILE):
        return jsonify({"error": "config.py not found"}), 404

    return jsonify(global_config)

@app.route("/all_metainfo", methods=["GET"])
def get_all_metainfo():
    if not os.path.exists(global_config["ALL_METAINFO_PATH"]):
        return jsonify({"error": "all_metainfo.json not found"}), 404

    data = load_json(global_config["ALL_METAINFO_PATH"])

    return jsonify(data)

@app.route("/testcase_metainfo", methods=["GET"])
def get_testcase_metainfo():
    if not os.path.exists(global_config["TESTCASE_METAINFO_PATH"]):
        return jsonify({"error": "testcase_metainfo.json not found"}), 404

    data = load_json(global_config["TESTCASE_METAINFO_PATH"])

    return jsonify(data)

@app.route("/function_metainfo", methods=["GET"])
def get_function_metainfo():
    if not os.path.exists(global_config["FUNCTION_METAINFO_PATH"]):
        return jsonify({"error": "function_metainfo.json not found"}), 404

    data = load_json(global_config["FUNCTION_METAINFO_PATH"])

    return jsonify(data)

@app.route("/udt_metainfo", methods=["GET"])
def get_udt_metainfo():
    if not os.path.exists(global_config["UDT_METAINFO_PATH"]):
        return jsonify({"error": "udt_metainfo.json not found"}), 404

    data = load_json(global_config["UDT_METAINFO_PATH"])

    return jsonify(data)

@app.route("/global_variable_metainfo", methods=["GET"])
def get_global_variable_metainfo():
    if not os.path.exists(global_config["GLOBAL_VARIABLE_METAINFO_PATH"]):
        return jsonify({"error": "global_variable_metainfo.json not found"}), 404

    data = load_json(global_config["GLOBAL_VARIABLE_METAINFO_PATH"])

    return jsonify(data)

@app.route("/function_similarity", methods=["GET"])
def get_function_similarity():
    if not os.path.exists(global_config["FUNCTION_SIMILARITY_PATH"]):
        return jsonify({"error": "function_similarity.json not found"}), 404

    data = load_json(global_config["FUNCTION_SIMILARITY_PATH"])

    return jsonify(data)

@app.route("/testcase_analysis_result", methods=["GET"])
def get_testcase_analysis_result():
    if not os.path.exists(global_config["TESTCASE_ANALYSIS_RESULT_PATH"]):
        return jsonify({"error": "testcase_analysis_result.json not found"}), 404

    data = load_json(global_config["TESTCASE_ANALYSIS_RESULT_PATH"])

    return jsonify(data)

@app.route("/context_analysis_result", methods=["GET"])
def get_context_analysis_result():
    if not os.path.exists(global_config["CONTEXT_ANALYSIS_RESULT_PATH"]):
        return jsonify({"error": "context_analysis_result.json not found"}), 404

    data = load_json(global_config["CONTEXT_ANALYSIS_RESULT_PATH"])

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
