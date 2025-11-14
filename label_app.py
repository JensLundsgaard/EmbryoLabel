from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import random
from pathlib import Path

app = Flask(__name__)

# Configuration
DATASET_DIR = Path("embryo_dataset")
TRUE_IMAGES_FILE = Path("true_images.txt")

# Create necessary directories
DATASET_DIR.mkdir(exist_ok=True)

# Image extensions to look for
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

# Cache for image list
_image_cache = None

# Label history (stack of last 10 labels)
# Each item is a dict: {'image_path': str, 'label': 'true'|'false'}
_label_history = []
MAX_HISTORY = 10


def get_all_images(use_cache=True):
    """Recursively find all images in the dataset directory."""
    global _image_cache

    if use_cache and _image_cache is not None:
        return _image_cache

    images = []
    if DATASET_DIR.exists():
        for root, dirs, files in os.walk(DATASET_DIR):
            for file in files:
                if Path(file).suffix.lower() in IMAGE_EXTENSIONS:
                    # Make path relative to DATASET_DIR
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, DATASET_DIR)
                    images.append(relative_path)

    _image_cache = images
    return images


def get_next_image():
    """Get a random unlabeled image from the dataset."""
    all_images = get_all_images()

    if not all_images:
        return None

    # Randomly select an image
    return random.choice(all_images)


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/next-image')
def next_image():
    """Get the next image to label."""
    image_path = get_next_image()

    if not image_path:
        return jsonify({'error': 'No images found in embryo_dataset'}), 404

    return jsonify({
        'image_path': image_path,
        'image_url': f'/image/{image_path}'
    })


@app.route('/image/<path:image_path>')
def serve_image(image_path):
    """Serve an image file."""
    # Construct the full path
    full_path = DATASET_DIR / image_path

    # Security check: ensure the path is within embryo_dataset
    try:
        full_path.resolve().relative_to(DATASET_DIR.resolve())
    except ValueError:
        return "Access denied", 403

    return send_from_directory(DATASET_DIR, image_path)


@app.route('/api/label', methods=['POST'])
def label_image():
    """Label an image as true or false."""
    global _label_history

    data = request.json
    image_path = data.get('image_path')
    label = data.get('label')  # 'true' or 'false'

    if not image_path or label not in ['true', 'false']:
        return jsonify({'error': 'Invalid request'}), 400

    # Construct full path from relative path
    source_path = DATASET_DIR / image_path

    if not source_path.exists():
        return jsonify({'error': 'Image not found'}), 404

    # If label is 'true', append to the text file
    if label == 'true':
        with open(TRUE_IMAGES_FILE, 'a') as f:
            f.write(f"{image_path}\n")

    # Add to history stack
    _label_history.append({
        'image_path': image_path,
        'label': label
    })

    # Keep only last MAX_HISTORY items
    if len(_label_history) > MAX_HISTORY:
        _label_history.pop(0)

    return jsonify({
        'success': True,
        'label': label,
        'image_path': image_path
    })


@app.route('/api/undo', methods=['POST'])
def undo_last():
    """Undo the last labeled image and return it for display."""
    global _label_history

    if not _label_history:
        return jsonify({'error': 'No labels to undo'}), 400

    try:
        # Pop the last label from history
        last_label = _label_history.pop()
        image_path = last_label['image_path']
        label = last_label['label']

        # If it was labeled 'true', remove it from the file
        if label == 'true':
            if TRUE_IMAGES_FILE.exists():
                with open(TRUE_IMAGES_FILE, 'r') as f:
                    lines = f.readlines()

                # Remove the last occurrence of this image path
                # Write back all lines except the last occurrence
                lines_reversed = lines[::-1]
                removed = False
                for i, line in enumerate(lines_reversed):
                    if line.strip() == image_path and not removed:
                        lines_reversed.pop(i)
                        removed = True
                        break

                with open(TRUE_IMAGES_FILE, 'w') as f:
                    f.writelines(lines_reversed[::-1])

        return jsonify({
            'success': True,
            'image_path': image_path,
            'image_url': f'/image/{image_path}',
            'label': label
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """Get labeling statistics."""
    true_count = 0
    if TRUE_IMAGES_FILE.exists():
        with open(TRUE_IMAGES_FILE, 'r') as f:
            true_count = len(f.readlines())

    remaining = len(get_all_images())

    return jsonify({
        'true': true_count,
        'remaining': remaining,
        'total': true_count + remaining
    })


if __name__ == '__main__':
    print("Starting Embryo Image Labeler Server...")
    print(f"Dataset directory: {DATASET_DIR.absolute()}")
    print(f"True images file: {TRUE_IMAGES_FILE.absolute()}")
    print("Server running at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
