from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

DETECT_TASKS = {}

# {
#   "detection_id": { type: str item: str, item_detection_image: [str], criteria: list[str], criteria_images: [str] }
# }

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Backend is running"})

@app.route('/detect', methods=['POST'])
def detect():
    """
    Receive an image and save it locally.
    Expects JSON with base64 encoded image.
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({"error": "No image provided"}), 400
        
        # Get base64 image data
        image_data = data['image']
        
        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"upload_{timestamp}.jpg"
        filepath = UPLOAD_DIR / filename
        
        # Save image locally
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        print(f"✅ Image saved: {filepath}")
        
        # TODO: Add detection logic here
        # For now, return mock response
        response = {
            "success": True,
            "message": "Image received successfully",
            "filename": filename,
            "filepath": str(filepath),
            "size_bytes": len(image_bytes),
            # Mock detection results
            "is_authentic": True,
            "confidence": 0.85,
            "detected_item": "Sample Item"
        }

        # TODO: use item_detection.py to analyze the item

        # TODO: use criteria.py to get the criteria for the item

        # TODO: return the criteria's camera angle and location

        # TODO: update the DETECT_TASKS with the detection_id (should be generated), item, item_detection_image, criteria
        
        # TODO: return the `detection_id` and criteria's camera angle and location
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def analyze_item(detection_id: str):
    """
    Analyze the item for the detection_id
    """
    pass

   # TODO: get detection_id, and the x number of images from requested criteria angle and location

   # TODO: use counterfeit.py to analyze the item, pass in the criteria's camera angle and location, and the item_detection_image

   # TODO: get the confidence score from the counterfeit.py analysis

   # TODO: return the results.


if __name__ == '__main__':
    print("🚀 Starting Flask backend...")
    print(f"📁 Upload directory: {UPLOAD_DIR.absolute()}")
    app.run(debug=True, port=5555, host='0.0.0.0')

