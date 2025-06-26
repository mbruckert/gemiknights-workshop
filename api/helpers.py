from PIL import Image, ImageDraw

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
