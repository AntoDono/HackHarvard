# To run this code you need to install the following dependencies:
# pip install google-genai pillow opencv-python

import os
from pathlib import Path
from google import genai
from PIL import Image
from dotenv import load_dotenv
import json
import cv2
import time
import numpy as np
from typing import Dict, List, Optional

load_dotenv()

def get_gemini_client():
    """Initialize and return Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY must be set in environment variables")
    return genai.Client(api_key=api_key)
    
def capture_image_with_timer(countdown_seconds: int = 5, save_path: str = "captured_product.jpg") -> str:
    """Capture an image from camera with countdown timer."""
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        raise RuntimeError("Could not open camera. Make sure a camera is connected.")
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print(f"Camera initialized. Starting {countdown_seconds}-second countdown...")
    print("Position your product in the camera view!")
    
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.release()
            cv2.destroyAllWindows()
            raise RuntimeError("Failed to read from camera")
        
        # Calculate remaining time
        elapsed_time = time.time() - start_time
        remaining_time = countdown_seconds - elapsed_time
        
        # Create a copy of the frame for display
        display_frame = frame.copy()
        
        if remaining_time > 0:
            # Draw countdown timer
            timer_text = f"Capturing in: {int(remaining_time) + 1}"
            
            # Get text size for centering
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2
            thickness = 3
            text_size = cv2.getTextSize(timer_text, font, font_scale, thickness)[0]
            
            # Calculate position for centered text
            text_x = (display_frame.shape[1] - text_size[0]) // 2
            text_y = 100
            
            # Draw background rectangle for better visibility
            cv2.rectangle(display_frame, 
                        (text_x - 20, text_y - text_size[1] - 20),
                        (text_x + text_size[0] + 20, text_y + 20),
                        (0, 0, 0), -1)
            
            # Draw countdown text
            cv2.putText(display_frame, timer_text, (text_x, text_y),
                       font, font_scale, (0, 255, 0), thickness)
            
            # Draw instruction text
            instruction_text = "Position your product and wait..."
            inst_text_size = cv2.getTextSize(instruction_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            inst_x = (display_frame.shape[1] - inst_text_size[0]) // 2
            inst_y = display_frame.shape[0] - 50
            
            cv2.rectangle(display_frame,
                        (inst_x - 10, inst_y - inst_text_size[1] - 10),
                        (inst_x + inst_text_size[0] + 10, inst_y + 10),
                        (0, 0, 0), -1)
            
            cv2.putText(display_frame, instruction_text, (inst_x, inst_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
        else:
            # Time's up! Show "CAPTURING!" message
            capture_text = "CAPTURING!"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 3
            thickness = 4
            text_size = cv2.getTextSize(capture_text, font, font_scale, thickness)[0]
            
            text_x = (display_frame.shape[1] - text_size[0]) // 2
            text_y = display_frame.shape[0] // 2
            
            cv2.rectangle(display_frame,
                        (text_x - 30, text_y - text_size[1] - 30),
                        (text_x + text_size[0] + 30, text_y + 30),
                        (0, 0, 255), -1)
            
            cv2.putText(display_frame, capture_text, (text_x, text_y),
                       font, font_scale, (255, 255, 255), thickness)
        
        # Display the frame
        cv2.imshow('Product Detection - Camera Feed', display_frame)
        
        # Check if countdown is finished
        if remaining_time <= 0:
            # Save the original frame (without overlay)
            cv2.imwrite(save_path, frame)
            print(f"Image captured and saved to: {save_path}")
            time.sleep(1)  # Show "CAPTURING!" message for 1 second
            break
        
        # Break on 'q' key press or window close
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            print("Capture cancelled by user")
            break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    
    # Check if file was actually saved
    if not Path(save_path).exists():
        raise RuntimeError("Failed to save captured image")
        
    return save_path
    

    
def detect_with_camera(max_attempts: int = 5) -> Dict:
    """Interactive camera detection with user choice after each attempt."""
    print(f"🎯 PRECISION DETECTION (up to {max_attempts} attempts)")
    print("=" * 50)
    
    best_result = None
    best_attempt = 0
    
    for attempt in range(1, max_attempts + 1):
        print(f"📸 ATTEMPT {attempt}/{max_attempts}")
        print("-" * 30)
        
        if attempt == 1:
            print("Position product clearly with brand/details visible.")
        
        try:
            # Capture image
            save_path = f"product_attempt_{attempt}.jpg"
            image_path = capture_image_with_timer(5, save_path)
            
            # Analyze with capture metadata
            capture_info = {
                "image_path": image_path,
                "capture_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "attempt": attempt
            }
            
            print("Analyzing captured image...")
            result = analyze_image(image_path, is_from_camera=True, capture_info=capture_info)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                # Still save as best result if it's the first attempt or better than previous
                if best_result is None:
                    best_result = result
                    best_attempt = attempt
            else:
                # Always update best result if no error
                best_result = result
                best_attempt = attempt
            
            # Show current detection status
            products = result.get("products", [])
            if "error" not in result and products:
                main_product = products[0]
                print(f"📊 Attempt {attempt}: Found {len(products)} product(s) - {main_product.get('name', 'Unknown')} ({main_product.get('confidence', 'Unknown')} confidence)")
            else:
                print(f"📊 Attempt {attempt}: {'Error occurred' if 'error' in result else 'No products detected'}")
            
            # Check if this is a successful detection
            detection_status = result.get("detection_status", "success")
            repositioning_needed = result.get("repositioning_request", {}).get("needed", False)
            
            if detection_status == "success" and not repositioning_needed:
                print("✅ EXACT PRODUCT IDENTIFIED!")
                return result
            
            # After attempt 1, give user choice to continue
            if attempt >= 1 and attempt < max_attempts:
                if detection_status == "needs_repositioning" and repositioning_needed:
                    repo_req = result["repositioning_request"]
                    print(f"\n🔄 REPOSITIONING SUGGESTED")
                    print(f"Reason: {repo_req.get('reason', 'Better view needed')}")
                    print(f"Instructions: {repo_req.get('instructions', 'Adjust position')}")
                    print()
                
                print("🤔 WHAT WOULD YOU LIKE TO DO?")
                print("1. Continue with another attempt (recommended if repositioning needed)")
                print("2. Stop here and use the best detection available")
                print(f"3. View current detection details")
                
                choice = input(f"\nChoose option (1-3) [Enter = Continue]: ").strip()
                
                if choice == "2":
                    print(f"\n✅ Using best detection from attempt {best_attempt}")
                    return best_result
                elif choice == "3":
                    print("\n" + "="*50)
                    print("📋 CURRENT DETECTION DETAILS:")
                    print("="*50)
                    print(get_product_summary(result))
                    print("\nPress ENTER to continue or type 'stop' to use this result...")
                    continue_choice = input().strip().lower()
                    if continue_choice == 'stop':
                        return result
                
                # Default (1) or Enter - continue to next attempt
                print(f"\n🔄 Continuing to attempt {attempt + 1}...")
                if repositioning_needed:
                    print("Please reposition your product as suggested above.")
                    print("Press ENTER when ready for next capture...")
                    input()
            
        except Exception as e:
            print(f"❌ Attempt {attempt} failed: {str(e)}")
            error_result = {"error": f"Attempt {attempt} error: {str(e)}", "products": []}
            if best_result is None:
                best_result = error_result
                best_attempt = attempt
    
    # If we reach here, all attempts completed
    print(f"\n🏁 All {max_attempts} attempts completed.")
    if best_result:
        print(f"✅ Returning best result from attempt {best_attempt}")
        return best_result
    
    return {"error": "All attempts failed with no usable results", "products": []}
    

    
def analyze_image(image_path: str, is_from_camera: bool = False, capture_info: Dict = None) -> Dict:
    """Analyze an image for exact product details with repositioning guidance."""
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Compact prompt for exact product identification
    prompt = """Return ONLY valid JSON. Identify EXACT products (not generic). Use "N/A" for missing fields.

    {
      "detection_status": "success" | "needs_repositioning",
      "repositioning_request": {"needed": true/false, "instructions": "specific instructions OR N/A", "reason": "reason OR N/A"},
      "products": [{
        "name": "EXACT product name OR N/A", "brand": "Brand OR N/A", "version": "Version/size OR N/A",
        "category": "Category OR N/A", "description": "Description OR N/A", "price": "Price OR N/A",
        "barcode": "Barcode OR N/A", "ingredients": "Ingredients OR N/A", "nutritional_info": "Nutrition OR N/A",
        "size": "Size OR N/A", "color": "Color OR N/A", "material": "Material OR N/A",
        "country_of_origin": "Origin OR N/A", "expiry_date": "Expiry OR N/A",
        "confidence": "High|Medium|Low", "identification_certainty": "Percentage OR N/A"
      }],
      "image_quality": "Quality assessment", "visibility_issues": ["Issues"], "detection_notes": "Notes"
    }

    GOOD: "Coca-Cola Classic 12oz can" BAD: "soda"
    If unclear: "needs_repositioning" with instructions like "Rotate to show label" or "Hold closer"
    """
    
    try:
        client = get_gemini_client()
        image = Image.open(image_path)
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=[prompt, image]
        )
        
        # Parse and validate JSON response
        response_text = response.text.strip()
        if response_text.startswith("```"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        result = json.loads(response_text)
        
        # Validate and fill missing fields
        validate_result(result)
        
        # Add capture info if from camera
        if is_from_camera and capture_info:
            result["capture_info"] = capture_info
        
        return result
        
    except json.JSONDecodeError as e:
        return create_error_result(f"JSON parsing failed: {str(e)}", response.text)
    except Exception as e:
        return create_error_result(f"Processing error: {str(e)}")
    
def validate_result(result: Dict) -> None:
    """Ensure all required fields are present with N/A defaults."""
    required_product_fields = [
        "name", "brand", "version", "category", "description", "price", 
        "barcode", "ingredients", "nutritional_info", "size", "color", 
        "material", "country_of_origin", "expiry_date", "confidence", 
        "identification_certainty"
    ]
    
    if "products" in result and result["products"]:
        for product in result["products"]:
            for field in required_product_fields:
                if field not in product or not product[field]:
                    product[field] = "N/A"
    
    if "repositioning_request" not in result:
        result["repositioning_request"] = {
            "needed": False, "instructions": "N/A", "reason": "N/A"
        }

def create_error_result(error_msg: str, raw_response: str = "") -> Dict:
    """Create standardized error result."""
    return {
        "error": error_msg,
        "raw_response": raw_response[:500] + "..." if len(raw_response) > 500 else raw_response,
        "detection_status": "needs_repositioning",
        "repositioning_request": {
            "needed": True,
            "instructions": "Try again with better lighting and clearer view",
            "reason": "Analysis error occurred"
        },
        "products": []
    }
    

    
def get_product_summary(detection_result: Dict) -> str:
    """Get a human-readable summary of detected products with repositioning info."""
    if "error" in detection_result:
        return f"❌ Error: {detection_result['error']}"
    
    summary = []
    
    # Handle repositioning status
    detection_status = detection_result.get("detection_status", "success")
    repositioning = detection_result.get("repositioning_request", {})
    
    if detection_status == "needs_repositioning":
        summary.append("🔄 REPOSITIONING NEEDED")
        summary.append(f"Reason: {repositioning.get('reason', 'Better view needed')}")
        summary.append(f"Instructions: {repositioning.get('instructions', 'Please adjust product position')}")
        summary.append("")
    
    if not detection_result.get("products"):
        if detection_status == "needs_repositioning":
            summary.append("⚠️ No exact products identified. Please follow repositioning instructions above.")
        else:
            summary.append("❌ No products detected in the image.")
        return "\n".join(summary)
    
    # Product details
    summary.append(f"🎯 EXACT PRODUCTS IDENTIFIED: {len(detection_result['products'])}")
    summary.append("")
    
    for i, product in enumerate(detection_result["products"], 1):
        # Product name with emphasis on specificity
        name = product.get('name', 'Unknown Product')
        certainty = product.get('identification_certainty', 'N/A')
        
        summary.append(f"{i}. 🏷️ {name}")
        
        if product.get('brand'):
            summary.append(f"   Brand: {product['brand']}")
        if product.get('version'):
            summary.append(f"   Version/Model: {product['version']}")
        if product.get('size'):
            summary.append(f"   Size: {product['size']}")
        if product.get('category'):
            summary.append(f"   Category: {product['category']}")
        if product.get('price'):
            summary.append(f"   Price: {product['price']}")
        if product.get('barcode'):
            summary.append(f"   Barcode: {product['barcode']}")
        
        # Confidence indicators
        confidence = product.get('confidence', 'Unknown')
        summary.append(f"   Detection Confidence: {confidence}")
        if certainty != 'N/A':
            summary.append(f"   Identification Certainty: {certainty}")
        
        summary.append("")
    
    # Additional info
    if detection_result.get("visibility_issues"):
        summary.append("⚠️ Visibility Issues Noted:")
        for issue in detection_result["visibility_issues"]:
            summary.append(f"   • {issue}")
        summary.append("")
    
    if detection_result.get("image_quality"):
        summary.append(f"📊 Image Quality: {detection_result['image_quality']}")
    
    return "\n".join(summary)


def main():
    """Main function to run the interactive product detection system."""
    try:
        print("🎯 PRECISION PRODUCT DETECTION")
        print("Detects EXACT products (not generic categories)")
        print("Examples: 'Coca-Cola Classic 12oz can' not just 'soda'")
        print("\n1. Interactive Detection (up to 5 attempts)")
        print("2. Single Capture")
        print("3. Quit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '3':
            print("Exiting...")
            return
        elif choice == '1':
            # Interactive detection with repositioning
            result = detect_with_camera(max_attempts=5)
        elif choice == '2':
            print("\n📸 SINGLE CAPTURE - Position product clearly!")
            if input("Press ENTER to start or 'q' to quit: ").strip().lower() == 'q':
                return
            result = detect_with_camera(max_attempts=1)
        else:
            print("Invalid choice. Using interactive mode...")
            result = detect_with_camera(max_attempts=5)
        
        # Display results
        print("\n🎯 FINAL RESULTS")
        
        if "error" in result:
            print(f"❌ Final Error: {result['error']}")
            if "raw_response" in result:
                print(f"Raw AI response: {result['raw_response']}")
        else:
            # Print capture info if available
            if "capture_info" in result:
                capture_info = result["capture_info"]
                print(f"📸 Final image captured at: {capture_info['capture_time']}")
                print(f"💾 Saved to: {capture_info['image_path']}")
                print()
            
            # Print detailed product summary
            print(get_product_summary(result))
            
            # Check for successful exact identification
            products = result.get("products", [])
            if products:
                exact_products = [p for p in products if p.get("confidence") in ["High", "Medium"]]
                if exact_products:
                    print(f"✅ SUCCESS: {len(exact_products)} exact product(s) identified!")
                else:
                    print("⚠️ Products detected but with low confidence.")
            
            # Offer detailed JSON view
            if input("\nSee technical details? (y/n): ").strip().lower() in ['y', 'yes']:
                print("\n📋 TECHNICAL DETAILS:")
                print(json.dumps(result, indent=2))
        
        # Option to detect another product
        if input("\n🔄 Detect another product? (y/n): ").strip().lower() in ['y', 'yes']:
            result2 = detect_with_camera(max_attempts=5)
            print("\n🎯 SECOND PRODUCT:")
            print(get_product_summary(result2))
        
        print("\n✨ Thanks for using Product Detection!")
        
    except KeyboardInterrupt:
        print("\n\nCapture interrupted by user. Cleaning up...")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Check: camera connection, dependencies (pip install google-genai pillow opencv-python), GEMINI_API_KEY")


if __name__ == "__main__":
    main()
