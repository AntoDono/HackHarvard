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
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask backend...")
    print(f"📁 Upload directory: {UPLOAD_DIR.absolute()}")
    app.run(debug=True, port=5555, host='0.0.0.0')

