from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
from PIL import Image, ImageDraw
import io
import base64
import json
import os
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Gemini client
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'heic', 'heif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_coordinates(bounding_boxes, width, height):
    """Convert normalized coordinates (0-1000) to absolute pixel coordinates"""
    converted_boxes = []
    for bbox in bounding_boxes:
        if 'box_2d' in bbox:
            box_2d = bbox['box_2d']
            # box_2d format: [ymin, xmin, ymax, xmax] normalized to 0-1000
            abs_ymin = int(box_2d[0] / 1000 * height)
            abs_xmin = int(box_2d[1] / 1000 * width)
            abs_ymax = int(box_2d[2] / 1000 * height)
            abs_xmax = int(box_2d[3] / 1000 * width)

            converted_boxes.append({
                'label': bbox.get('label', 'difference'),
                'confidence': bbox.get('confidence', 1.0),
                # [x1, y1, x2, y2]
                'bounding_box': [abs_xmin, abs_ymin, abs_xmax, abs_ymax]
            })
    return converted_boxes


def create_difference_image(image1, image2, bounding_boxes):
    """Create an image highlighting the differences with bounding boxes"""
    # Use the first image as base
    result_image = image1.copy()
    draw = ImageDraw.Draw(result_image)

    # Draw bounding boxes on the differences
    for bbox in bounding_boxes:
        coords = bbox['bounding_box']  # [x1, y1, x2, y2]
        # Draw rectangle only (no text labels)
        draw.rectangle(coords, outline='red', width=3)

    return result_image


def detect_differences(image1, image2):
    """Use Gemini API with function calling to detect differences between two images"""
    try:
        # Define the function declaration for detecting differences
        detect_differences_function = {
            "name": "report_image_differences",
            "description": "Reports all differences found between two images with precise bounding box coordinates and detailed descriptions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "differences": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {
                                    "type": "string",
                                    "description": "Detailed description of the specific difference found"
                                },
                                "box_2d": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "description": "Bounding box coordinates in format [ymin, xmin, ymax, xmax] normalized to 0-1000. IT'S VERY IMPORTANT THAT YOU DRAW THE CORRECT BOUNDING BOXES!!"
                                },
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0.1,
                                    "maximum": 1.0,
                                    "description": "Confidence score for this difference detection"
                                }
                            },
                            "required": ["label", "box_2d", "confidence"]
                        },
                        "description": "Array of all differences found between the two images"
                    }
                },
                "required": ["differences"]
            }
        }

        prompt = """
        You are an expert at spot-the-difference puzzles. Carefully examine these two images pixel by pixel and identify ALL differences between them, no matter how small or subtle.

        Look for these types of differences:
        - Objects added, removed, or moved
        - Color changes (even slight variations)
        - Size changes (objects made bigger/smaller)
        - Orientation changes (rotated, flipped)
        - Text changes
        - Number of items changed (more/fewer objects)

        For each difference found, use the report_image_differences function to provide:
        1. A detailed descriptive label explaining exactly what changed
        2. The bounding box coordinates in the format [ymin, xmin, ymax, xmax] normalized to 0-1000. IT'S VERY IMPORTANT THAT YOU DRAW THE CORRECT BOUNDING BOXES!!
        3. A confidence score between 0.1 and 1.0

        Be exhaustive and thorough - find every single difference possible! Only report differences that you are 100% sure are actual differences.
        """

        # Configure tools and function calling
        tools = types.Tool(function_declarations=[detect_differences_function])
        config = types.GenerateContentConfig(
            tools=[tools],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode='ANY')
            ),
            thinking_config=types.ThinkingConfig(thinking_budget=3000)
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image1, image2],
            config=config
        )

        # Check if the model made a function call
        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call

            if function_call.name == "report_image_differences":
                differences = function_call.args.get("differences", [])

                # Log the results for debugging
                print(
                    f"Gemini found {len(differences)} differences via function calling")
                for i, diff in enumerate(differences):
                    print(f"Difference {i+1}: {diff.get('label', 'No label')}")

                return differences
            else:
                print(f"Unexpected function call: {function_call.name}")
                return []
        else:
            print("No function call found in response")
            return []

    except Exception as e:
        print(f"Error detecting differences: {str(e)}")
        return []


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
    # Check if API key is set
    if not os.getenv('GOOGLE_API_KEY'):
        print("Warning: GOOGLE_API_KEY environment variable not set!")
        print("Please set your Gemini API key: export GOOGLE_API_KEY='your-api-key-here'")

    app.run(debug=True, host='0.0.0.0', port=5000)
