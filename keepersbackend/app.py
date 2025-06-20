from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
from cleaning_check import inspect_cleaning_job

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ANNOTATED_FOLDER = 'annotated'
PREVIEW_FOLDER = os.path.join(ANNOTATED_FOLDER, 'previews')

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ANNOTATED_FOLDER, exist_ok=True)
os.makedirs(PREVIEW_FOLDER, exist_ok=True)

@app.route('/upload-folders', methods=['POST'])
def upload_folders():
    ref_files = request.files.getlist('reference[]')
    post_files = request.files.getlist('postclean[]')

    if len(ref_files) != len(post_files):
        return jsonify({'error': 'Mismatched number of reference and postclean images'}), 400

    results = []

    for i, (ref, post) in enumerate(zip(ref_files, post_files), 1):
        ref_path = os.path.join(UPLOAD_FOLDER, f'ref_{i}.jpg')
        post_path = os.path.join(UPLOAD_FOLDER, f'post_{i}.jpg')
        ref.save(ref_path)
        post.save(post_path)

        result = inspect_cleaning_job(ref_path, post_path, job_id=f'batch_job_{i}')
        result['annotated_image_url'] = f"/annotated/{os.path.basename(result['annotated_image'])}"

        results.append(result)

    return jsonify({'results': results})


@app.route('/inspect', methods=['POST'])
def inspect():
    ref_file = request.files['reference']
    post_file = request.files['postclean']

    ref_path = os.path.join(UPLOAD_FOLDER, 'reference.jpg')
    post_path = os.path.join(UPLOAD_FOLDER, 'postclean.jpg')

    ref_file.save(ref_path)
    post_file.save(post_path)

    result = inspect_cleaning_job(ref_path, post_path, job_id='single_job')

    result['annotated_image_url'] = f"/annotated/{os.path.basename(result['annotated_image'])}"
    #result['ref_preview_url'] = f"/annotated/previews/{os.path.basename(result['ref_preview'])}"
    #result['post_preview_url'] = f"/annotated/previews/{os.path.basename(result['post_preview'])}"

    return jsonify(result)


@app.route('/annotated/<path:filename>')
def serve_annotated(filename):
    return send_from_directory(ANNOTATED_FOLDER, filename)


@app.route('/annotated/previews/<filename>')
def serve_preview(filename):
    return send_from_directory(PREVIEW_FOLDER, filename)

@app.route('/uploads/<filename>')
def serve_uploaded(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    print(f"[INFO] Starting Flask server at http://127.0.0.1:5000")
    app.run(debug=True)
