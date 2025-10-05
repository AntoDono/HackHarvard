from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
import requests
from item_detection import analyze_image, get_price, extract_product_name
from criteria import criteria as get_criteria
from counterfeit import counterfeit
from generate_real_images import ReverseImageSearcher
from upload_image import upload_image_to_supabase
from person import research_person_fakeness
from fact_check import fact_check
from image_similarity_scores import ComparisonAnalyzer
from ai_detection.model import DeepfakeModel
from ai_detection.inference import is_deepfake

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# ============================================
# CONFIGURATION - Adjust these as needed
# ============================================
DEEPFAKE_CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence (0.0-1.0) to flag as AI-generated
# ============================================

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
SEARCHER = ReverseImageSearcher()
SIMILARITY_ANALYZER = ComparisonAnalyzer()

# Deepfake detection will be handled by the is_deepfake function

DETECT_TASKS = {}

def download_image(url: str, save_path: Path) -> bool:
    """Download an image from URL and save it to the specified path."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded image from {url} to {save_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to download image from {url}: {str(e)}")
        return False

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
        
        # 🤖 DEEPFAKE DETECTION - Check if image is AI-generated before proceeding
        print("🔍 Running deepfake detection...")
        try:
            # Upload image to get public URL for API
            image_url = upload_image_to_supabase(str(filepath), custom_filename=filename)
            if image_url:
                print(f"📤 Uploaded image for detection: {image_url}")
                
                # Use our trained deepfake detection model
                try:
                    # Download image temporarily for local processing
                    temp_image_path = UPLOAD_DIR / f"temp_{filename}"
                    if download_image(image_url, temp_image_path):
                        # Use our model for detection with configured threshold
                        result = is_deepfake(str(temp_image_path), confidence_threshold=DEEPFAKE_CONFIDENCE_THRESHOLD)
                        
                        # Extract results
                        is_deepfake_result = result['is_deepfake']
                        probability = result['raw_confidence']
                        prediction = result['prediction']
                        confidence = result['confidence']
                        
                        per_model = {'custom_model': probability}
                        
                        print(f"🤖 Deepfake detection result: {probability:.2%}")
                        print(f"🤖 Detection details: {per_model}")
                        print(f"🤖 Model prediction: {prediction} (confidence: {confidence:.2%})")
                        
                        # Clean up temp file
                        temp_image_path.unlink(missing_ok=True)
                    else:
                        raise Exception("Failed to download image for processing")
                except Exception as e:
                    print(f"⚠️  Custom model detection failed: {e}")
                    # Fallback to SightEngine API (placeholder - implement if needed)
                    print("⚠️  Fallback API not implemented")
                    is_deepfake_result = None
                    probability = None
                    per_model = {}
            
            else:
                print("⚠️  Failed to upload image for detection")
                is_deepfake_result = None
                probability = None
                per_model = {}
            
            # If detected as deepfake (probability >= threshold), return early with deepfake info
            if is_deepfake_result and probability is not None and probability >= DEEPFAKE_CONFIDENCE_THRESHOLD:
                print(f"⚠️  DEEPFAKE DETECTED with {probability:.2%} confidence")
                
                response = {
                    "success": True,
                    "is_deepfake": True,
                    "deepfake_detection": {
                        "is_deepfake": is_deepfake_result,
                        "probability": probability,
                        "confidence_level": "high" if probability > 0.75 else "medium" if probability > 0.5 else "low",
                        "per_model_results": [
                            {
                                "model": model_name.replace("_image", "").replace("_", " ").title(),
                                "probability": prob,
                                "detected_as_fake": prob > 0.5 if prob is not None else None
                            }
                            for model_name, prob in per_model.items()
                        ],
                        "average_probability": probability,
                        "message": "This image appears to be AI-generated or manipulated.",
                        "warning": "The content in this image may not be authentic."
                    },
                    "filename": filename
                }
                
                return jsonify(response), 200
            
            # If not a deepfake, log and continue with normal detection
            if probability is not None:
                print(f"✅ Image appears authentic ({(1-probability):.2%} confidence)")
            
        except FileNotFoundError as e:
            # Models not found - log warning but continue
            print(f"⚠️  Deepfake detection skipped: {str(e)}")
            print("   Continuing with normal detection flow...")
        except Exception as e:
            # Other errors - log but don't stop the flow
            print(f"⚠️  Deepfake detection error: {str(e)}")
            print("   Continuing with normal detection flow...")
        
        # Use item_detection.py to analyze the image
        detection_result = analyze_image(str(filepath), allow_repositioning=False)
        
        # Check if repositioning is needed
        if detection_result.get("needs_repositioning"):
            response = {
                "success": False,
                "needs_repositioning": True,
                "repositioning_instructions": detection_result.get("repositioning_instructions", "Please reposition the image"),
                "filename": filename
            }
            return jsonify(response), 200
        
        # Get the detected item information
        item_type = detection_result.get("type", "other")
        item_name = detection_result.get("name", "")
        print(f"✅ Detected item type: {item_type}")
        print(f"✅ Detected item name: {item_name}")
        
        if not item_name:
            return jsonify({
                "success": False,
                "error": "Could not identify the item in the image"
            }), 400
        
        # Generate unique detection_id
        detection_id = str(uuid.uuid4())
        
        # Branch based on detected type
        if item_type == "product":
            print("🛍️  Product detected - following product workflow")
            
            # Use reverse image search to find product URL and images
            product_url = None
            product_image = None
            product_image_path = None
            uploaded_image_url = upload_image_to_supabase(str(filepath))    
            search_results = SEARCHER.search_by_image_url(uploaded_image_url, max_results=10)
            
            if search_results:
                # Get top result with highest trust score
                top_result = max(search_results, key=lambda x: x.get('trust_score', 0))
                product_url = top_result.get('link', '')
                product_image = top_result.get('thumbnail', '')
                product_title = top_result.get('title', '')
                
                product_name = extract_product_name(product_title)
                if product_name:
                    item_name = product_name
                print(f"✅ Found product URL: {product_url}")
                print(f"✅ Found product image: {product_image}")
                print(f"✅ Found product name: {product_title}")
                
                # Download the product image
                if product_image:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    product_filename = f"product_{detection_id}_{timestamp}.jpg"
                    product_image_path = UPLOAD_DIR / product_filename
                    
                    if download_image(product_image, product_image_path):
                        product_image_path = str(product_image_path)
                    else:
                        product_image_path = None
            else:
                print("⚠️  No search results found")
            
            price_range = get_price(item_name)
        
            # Store basic detection data (without criteria yet)
            DETECT_TASKS[detection_id] = {
                "item": item_name,
                "item_type": item_type,
                "item_detection_image": str(filepath),
                "detection_details": detection_result,
                "product_url": product_url,
                "product_image": product_image,
                "product_image_path": product_image_path,
                "price_range": price_range,
                "criteria": None,
                "location_angle": None,
                "detailed_criteria": None
            }
            
            # Return detection info with product URL, image, and price range
            response = {
                "success": True,
                "detection_id": detection_id,
                "item": item_name,
                "item_type": item_type,
                "confidence": detection_result.get("confidence", "Unknown"),
                "description": detection_result.get("description", ""),
                "product_url": product_url,
                "product_image": product_image,
                "price_range": price_range,
                "filename": filename
            }
            
            return jsonify(response), 200
            
        elif item_type == "person":
            print("👤 Person detected - waiting for user to provide name")
            
            # Store basic detection data (waiting for user input)
            DETECT_TASKS[detection_id] = {
                "item": item_name,
                "item_type": item_type,
                "item_detection_image": str(filepath),
                "detection_details": detection_result,
                "awaiting_person_input": True
            }
            
            # Return detection info and prompt for user input
            response = {
                "success": True,
                "detection_id": detection_id,
                "item_type": item_type,
                "confidence": detection_result.get("confidence", "Unknown"),
                "description": detection_result.get("description", ""),
                "image_path": filename,
                "awaiting_person_input": True,
                "message": "Person detected. Please provide their name and any additional information."
            }
            
            return jsonify(response), 200
            
        elif item_type == "text":
            print("📄 Text/document detected - performing fact check")
            
            # Perform fact check on the image
            fact_check_result = fact_check(str(filepath))
            
            # Store detection data
            DETECT_TASKS[detection_id] = {
                "item": item_name,
                "item_type": item_type,
                "item_detection_image": str(filepath),
                "detection_details": detection_result,
                "fact_check_result": fact_check_result
            }
            
            # Return fact check results
            response = {
                "success": True,
                "detection_id": detection_id,
                "item": item_name,
                "item_type": item_type,
                "confidence": detection_result.get("confidence", "Unknown"),
                "description": detection_result.get("description", ""),
                "filename": filename,
                "fact_check": fact_check_result
            }
            
            return jsonify(response), 200
            
        else:  # "other"
            print("❓ Other content detected - using Gemini analysis as fallback")
            
            # Use Gemini to analyze the image
            from ai_content import analyze_other_content
            gemini_analysis = analyze_other_content(str(filepath), item_name)
            
            # Log the analysis
            print(f"✅ Gemini Analysis: {gemini_analysis.get('title', 'N/A')}")
            print(f"   Category: {gemini_analysis.get('category', 'Unknown')}")
            print(f"   Description: {gemini_analysis.get('description', 'N/A')[:100]}...")
            
            # Store detection data
            DETECT_TASKS[detection_id] = {
                "item": item_name,
                "item_type": item_type,
                "item_detection_image": str(filepath),
                "detection_details": detection_result,
                "gemini_analysis": gemini_analysis
            }
            
            # Return success with basic info (frontend doesn't need to handle this specially)
            response = {
                "success": True,
                "detection_id": detection_id,
                "item": item_name,
                "item_type": item_type,
                "confidence": detection_result.get("confidence", "Unknown"),
                "description": gemini_analysis.get("description", detection_result.get("description", "")),
                "filename": filename,
                "message": f"Analyzed: {gemini_analysis.get('title', item_name)}"
            }
            
            return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/research_person', methods=['POST'])
def research_person():
    """
    Research a person after user provides their name.
    Expects JSON with detection_id, person_name, and optional additional_info.
    """
    try:
        data = request.get_json()
        
        if not data or 'detection_id' not in data or 'person_name' not in data:
            return jsonify({"error": "Missing detection_id or person_name"}), 400
        
        detection_id = data['detection_id']
        person_name = data['person_name']
        additional_info = data.get('additional_info', '')
        
        # Check if detection_id exists
        if detection_id not in DETECT_TASKS:
            return jsonify({"error": "Detection ID not found"}), 404
        
        task = DETECT_TASKS[detection_id]
        
        # Verify this is a person detection
        if task.get("item_type") != "person":
            return jsonify({"error": "This detection is not for a person"}), 400
        
        print(f"🔍 Researching person: {person_name}")
        if additional_info:
            print(f"📝 Additional context: {additional_info}")
        
        # Combine person_name with additional_info for more context
        search_query = f"{person_name} {additional_info}".strip()
        
        # Research the person using person.py
        person_research = research_person_fakeness(search_query)
        
        # Update task with research results
        DETECT_TASKS[detection_id]["person_name"] = person_name
        DETECT_TASKS[detection_id]["additional_info"] = additional_info
        DETECT_TASKS[detection_id]["person_research"] = person_research
        DETECT_TASKS[detection_id]["awaiting_person_input"] = False
        
        # Return research results
        response = {
            "success": True,
            "detection_id": detection_id,
            "person_name": person_name,
            "person_research": person_research
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/criteria/<detection_id>', methods=['POST'])
def get_criteria_for_detection(detection_id):
    """
    Step 2: Get authentication criteria for a detected item (product workflow).
    Accepts optional brand parameter in request body.
    """
    try:
        # Check if detection_id exists
        if detection_id not in DETECT_TASKS:
            return jsonify({"error": "Detection ID not found"}), 404
        
        task = DETECT_TASKS[detection_id]
        item_name = task["item"]
        
        # Get optional brand from request body
        data = request.get_json() if request.is_json else {}
        brand = data.get('brand', '').strip() if data else ''
        
        # If brand specified, prepend to item name
        if brand:
            item_name_with_brand = f"{brand} {item_name}"
            print(f"🏷️  Brand specified: {brand}, using '{item_name_with_brand}' for criteria")
            task["brand"] = brand
        else:
            item_name_with_brand = item_name
        
        # Get criteria if not already cached in the task
        if task["criteria"] is None:
            criteria_data = get_criteria(item_name_with_brand)
            
            # Update task with criteria (both simple and detailed formats)
            DETECT_TASKS[detection_id]["criteria"] = criteria_data.get("criteria", [])
            DETECT_TASKS[detection_id]["location_angle"] = criteria_data.get("location_angle", [])
            DETECT_TASKS[detection_id]["detailed_criteria"] = criteria_data.get("detailed_criteria", [])
        
        response = {
            "success": True,
            "detection_id": detection_id,
            "item": item_name,
            "location_angle": DETECT_TASKS[detection_id]["location_angle"],
            "detailed_criteria": DETECT_TASKS[detection_id].get("detailed_criteria", [])
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
        
        # Calculate initial scan similarity between product image and detection image
        initial_scan = None
        if task.get("product_image_path") and os.path.exists(task["product_image_path"]):
            try:
                print(f"🔍 Calculating similarity between product image and detection image...")
                similarity_result = SIMILARITY_ANALYZER.compare_images(
                    task["product_image_path"],
                    task["item_detection_image"],
                    threshold=0.7
                )
                
                if "error" not in similarity_result:
                    initial_scan = {
                        "similarity_score": similarity_result.get("similarity_score", 0),
                        "match_status": similarity_result.get("match_status", "UNKNOWN"),
                        "confidence": similarity_result.get("analysis", {}).get("confidence", "Unknown"),
                        "interpretation": similarity_result.get("analysis", {}).get("interpretation", ""),
                        "recommendation": similarity_result.get("analysis", {}).get("recommendation", ""),
                        "counterfeit_risk": similarity_result.get("analysis", {}).get("counterfeit_risk", "Unknown")
                    }
                    print(f"✅ Initial scan similarity: {initial_scan['similarity_score']:.3f}")
                else:
                    print(f"⚠️  Similarity calculation error: {similarity_result.get('error')}")
            except Exception as e:
                print(f"⚠️  Failed to calculate similarity: {str(e)}")
        
        # Use counterfeit.py to analyze
        print(f"Analyzing {task['item']} with {len(all_images)} images...")
        analysis_result = counterfeit(task["item"], criteria_data, all_images)
        
        # Store results in task
        DETECT_TASKS[detection_id]["analysis_result"] = analysis_result
        DETECT_TASKS[detection_id]["criteria_images"] = saved_image_paths
        DETECT_TASKS[detection_id]["initial_scan"] = initial_scan
        
        # Return the results
        response = {
            "success": True,
            "detection_id": detection_id,
            "item": task["item"],
            "is_authentic": analysis_result.get("is_authentic"),
            "overall_confidence": analysis_result.get("overall_confidence"),
            "criteria_results": analysis_result.get("criteria_results"),
            "summary": analysis_result.get("summary"),
            "initial_scan": initial_scan
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

