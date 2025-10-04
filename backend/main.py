from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
import uuid
from datetime import datetime
from pathlib import Path
from item_detection import analyze_product_from_image
from criteria import criteria as get_criteria
from counterfeit import counterfeit
from generate_real_images import ReverseImageSearcher

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

DETECT_TASKS = {}

# {
#   "detection_id": { 
#       "item": str, 
#       "item_detection_image": str, 
#       "criteria": list[str], 
#       "location_angle": list[str],
#       "product_details": dict,
#       "criteria_images": list[str],  # populated after /analyze
#       "analysis_result": dict  # populated after /analyze
#   }
# }

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Backend is running"})

@app.route('/detect', methods=['POST'])
def detect():
    """
    Step 1: Receive an image, detect the item, and return basic info.
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
        
        # Use item_detection.py to analyze the item
        detection_result = analyze_product_from_image(str(filepath))
        
        # Check if repositioning is needed
        if "repositioning instructions" in detection_result:
            response = {
                "success": False,
                "needs_repositioning": True,
                "repositioning_instructions": detection_result["repositioning instructions"],
                "filename": filename
            }
            return jsonify(response), 200
        
        # Product detected successfully
        product = detection_result.get("product", {})
        item_name = f"{product.get('brand', '')} {product.get('name', '')}".strip()
        
        if not item_name:
            return jsonify({
                "success": False,
                "error": "Could not identify the product"
            }), 400
        
        # Generate unique detection_id
        detection_id = str(uuid.uuid4())
        
        # Use reverse image search to find product URL and images
        product_url = None
        product_image = None
        try:
            print(f"🔍 Searching for product info using reverse image search...")
            searcher = ReverseImageSearcher()
            search_results = searcher.search_by_local_image(str(filepath), max_results=10)
            
            if search_results:
                # Get top result with highest trust score
                top_result = max(search_results, key=lambda x: x.get('trust_score', 0))
                product_url = top_result.get('link', '')
                product_image = top_result.get('thumbnail', '')
                
                print(f"✅ Found product URL: {product_url}")
                print(f"✅ Found product image: {product_image}")
            else:
                print("⚠️  No search results found")
        except Exception as e:
            print(f"⚠️  Error in reverse image search: {e}")
            # Continue without product URL/image if search fails
        
        # Store basic detection data (without criteria yet)
        DETECT_TASKS[detection_id] = {
            "item": item_name,
            "item_detection_image": str(filepath),
            "product_details": product,
            "product_url": product_url,
            "product_image": product_image,
            "criteria": None,
            "location_angle": None
        }
        
        # Return detection info with product URL and image
        response = {
            "success": True,
            "detection_id": detection_id,
            "item": item_name,
            "product_name": item_name,
            "product_url": product_url,
            "product_image": product_image,
            "product_details": product,
            "filename": filename
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/criteria/<detection_id>', methods=['GET'])
def get_criteria_for_detection(detection_id):
    """
    Step 2: Get authentication criteria for a detected item.
    """
    try:
        # Check if detection_id exists
        if detection_id not in DETECT_TASKS:
            return jsonify({"error": "Detection ID not found"}), 404
        
        task = DETECT_TASKS[detection_id]
        item_name = task["item"]
        
        # Get criteria if not already cached in the task
        if task["criteria"] is None:
            print(f"Getting criteria for: {item_name}")
            criteria_data = get_criteria(item_name)
            
            # Update task with criteria
            DETECT_TASKS[detection_id]["criteria"] = criteria_data.get("criteria", [])
            DETECT_TASKS[detection_id]["location_angle"] = criteria_data.get("location_angle", [])
        
        response = {
            "success": True,
            "detection_id": detection_id,
            "item": item_name,
            "location_angle": DETECT_TASKS[detection_id]["location_angle"]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/analyze/<detection_id>', methods=['POST'])
def analyze_item(detection_id: str):
    """
    Step 3: Analyze the item with criteria images.
    Expects JSON with array of base64 encoded images for each criterion.
    """
    try:
        # Check if detection_id exists
        if detection_id not in DETECT_TASKS:
            return jsonify({"error": "Detection ID not found"}), 404
        
        task = DETECT_TASKS[detection_id]
        
        # Validate that criteria exists
        if task["criteria"] is None or task["location_angle"] is None:
            return jsonify({"error": "Criteria not fetched yet. Call /criteria endpoint first."}), 400
        
        data = request.get_json()
        
        if not data or 'images' not in data:
            return jsonify({"error": "No images provided"}), 400
        
        # Get base64 images array
        base64_images = data['images']
        
        if not isinstance(base64_images, list):
            return jsonify({"error": "Images must be an array"}), 400
        
        # Save all criteria images
        saved_image_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for idx, image_data in enumerate(base64_images):
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            # Generate filename
            filename = f"criteria_{detection_id}_{timestamp}_{idx}.jpg"
            filepath = UPLOAD_DIR / filename
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            saved_image_paths.append(str(filepath))
            print(f"✅ Criteria image {idx + 1} saved: {filepath}")
        
        # Prepare criteria data for counterfeit analysis
        criteria_data = {
            "criteria": task["criteria"],
            "location_angle": task["location_angle"]
        }
        
        # Add the original detection image to the analysis
        all_images = [task["item_detection_image"]] + saved_image_paths
        
        # Use counterfeit.py to analyze
        print(f"Analyzing {task['item']} with {len(all_images)} images...")
        analysis_result = counterfeit(task["item"], criteria_data, all_images)
        
        # Store results in task
        DETECT_TASKS[detection_id]["analysis_result"] = analysis_result
        DETECT_TASKS[detection_id]["criteria_images"] = saved_image_paths
        
        # Return the results
        response = {
            "success": True,
            "detection_id": detection_id,
            "item": task["item"],
            "is_authentic": analysis_result.get("is_authentic"),
            "overall_confidence": analysis_result.get("overall_confidence"),
            "criteria_results": analysis_result.get("criteria_results"),
            "summary": analysis_result.get("summary")
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("🚀 Starting Flask backend...")
    print(f"📁 Upload directory: {UPLOAD_DIR.absolute()}")
    print(f"🌐 Running on {host}:{port}")
    
    app.run(debug=debug, port=port, host=host)

