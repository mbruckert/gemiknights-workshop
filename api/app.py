from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import base64
import os
import dotenv
from helpers import allowed_file, convert_coordinates, create_difference_image
from ai import detect_differences_with_ai

dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


def detect_differences(image1, image2):
    """Wrapper function that uses the AI module to detect differences between two images"""
    return detect_differences_with_ai(image1, image2)


@app.route('/detect_differences', methods=['POST'])
def detect_differences_endpoint():
    try:
        # Check if both images are provided
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({'error': 'Both image1 and image2 are required'}), 400

        file1 = request.files['image1']
        file2 = request.files['image2']

        # Check if files are selected
        if file1.filename == '' or file2.filename == '':
            return jsonify({'error': 'Both images must be selected'}), 400

        # Check file extensions
        if not (allowed_file(file1.filename) and allowed_file(file2.filename)):
            return jsonify({'error': 'Invalid file format. Supported formats: PNG, JPG, JPEG, WEBP, HEIC, HEIF'}), 400

        # Load and process images
        image1 = Image.open(file1.stream).convert('RGB')
        image2 = Image.open(file2.stream).convert('RGB')

        # Resize images if they're too large (for better performance)
        max_size = (1024, 1024)
        image1.thumbnail(max_size, Image.Resampling.LANCZOS)
        image2.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Detect differences using Gemini API
        differences = detect_differences(image1, image2)

        if not differences:
            return jsonify({
                'message': 'No differences detected',
                'differences': [],
                'difference_image': None
            })

        # Convert coordinates to absolute pixel values
        width, height = image1.size
        converted_differences = convert_coordinates(differences, width, height)

        # Create difference image with bounding boxes
        difference_image = create_difference_image(
            image1, image2, converted_differences)

        # Convert difference image to base64 for response
        buffer = io.BytesIO()
        difference_image.save(buffer, format='PNG')
        buffer.seek(0)
        difference_image_b64 = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            'message': f'Found {len(converted_differences)} difference(s)',
            'differences': converted_differences,
            'difference_image': f'data:image/png;base64,{difference_image_b64}',
            'image_dimensions': {'width': width, 'height': height}
        })

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
