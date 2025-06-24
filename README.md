# Spot-the-Difference App

A full-stack application with a Flask API backend that uses Google's Gemini AI to detect differences between two spot-the-difference images, and a React frontend for easy image upload and visualization.

## Features

- Modern React frontend with drag-and-drop image upload
- Upload two images via multipart/form-data
- Automatically detect differences using Gemini 2.5 Flash
- Return bounding box coordinates for each difference
- Generate annotated image with differences highlighted
- Support for multiple image formats (PNG, JPG, JPEG, WEBP, HEIC, HEIF)
- Real-time results with visual difference highlighting

## Setup

### Backend (Flask API)

1. Navigate to the API directory:

```bash
cd api
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Set your Google Gemini API key:

```bash
export GOOGLE_API_KEY='your-gemini-api-key-here'
```

4. Run the Flask application:

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend (React Vite)

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install Node.js dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Running Both Services

To run the complete application:

1. **Terminal 1** - Start the backend:

```bash
cd api
python app.py
```

2. **Terminal 2** - Start the frontend:

```bash
cd frontend
npm run dev
```

Then open your browser to `http://localhost:5173` to use the application.

## API Endpoints

### POST /detect_differences

Upload two images to detect differences between them.

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Fields:
  - `image1`: First image file
  - `image2`: Second image file

**Response:**

```json
{
  "message": "Found 3 difference(s)",
  "differences": [
    {
      "label": "missing red balloon",
      "confidence": 0.95,
      "bounding_box": [120, 80, 180, 140]
    }
  ],
  "difference_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "image_dimensions": {
    "width": 800,
    "height": 600
  }
}
```

**Bounding Box Format:**

- `[x1, y1, x2, y2]` where (x1, y1) is top-left corner and (x2, y2) is bottom-right corner
- Coordinates are in absolute pixels relative to the input image dimensions

## Usage Examples

### Using curl:

```bash
curl -X POST \
  -F "image1=@image1.jpg" \
  -F "image2=@image2.jpg" \
  http://localhost:5000/detect_differences
```

### Using Python requests:

```python
import requests

with open('image1.jpg', 'rb') as f1, open('image2.jpg', 'rb') as f2:
    files = {
        'image1': f1,
        'image2': f2
    }
    response = requests.post('http://localhost:5000/detect_differences', files=files)
    result = response.json()
    print(result)
```

### Using JavaScript (fetch):

```javascript
const formData = new FormData();
formData.append("image1", image1File);
formData.append("image2", image2File);

fetch("http://localhost:5000/detect_differences", {
  method: "POST",
  body: formData,
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Missing images, invalid file format, or other client errors
- `500 Internal Server Error`: Server-side processing errors

## Supported Image Formats

- PNG (image/png)
- JPEG (image/jpeg)
- WEBP (image/webp)
- HEIC (image/heic)
- HEIF (image/heif)

## Limitations

- Maximum file size: 16MB per image
- Images are automatically resized to 1024x1024 pixels for processing
- Requires a valid Google Gemini API key

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create a new API key
4. Set the API key as an environment variable: `export GOOGLE_API_KEY='your-key-here'`
