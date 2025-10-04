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

class ProductDetector:
    """
    A streamlined class to detect exact products from images or camera with repositioning guidance.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Gemini API key."""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment variables")
        
        self.client = genai.Client(api_key=self.api_key)
    
    def capture_image_with_timer(self, countdown_seconds: int = 5, save_path: str = "captured_product.jpg") -> str:
        """
        Capture an image from the camera with a countdown timer.
        
        Args:
            countdown_seconds: Number of seconds to count down before capture
            save_path: Path where to save the captured image
            
        Returns:
            Path to the saved image file
        """
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
    

    
    def detect_with_camera(self, max_attempts: int = 5) -> Dict:
        """
        Interactive camera detection with user choice after each attempt.
        
        Args:
            max_attempts: Maximum capture attempts
            
        Returns:
            Final detection result
        """
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
                image_path = self.capture_image_with_timer(5, save_path)
                
                # Analyze with capture metadata
                capture_info = {
                    "image_path": image_path,
                    "capture_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "attempt": attempt
                }
                
                print("Analyzing captured image...")
                result = self.analyze_image(image_path, is_from_camera=True, capture_info=capture_info)
                
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
                self._show_attempt_summary(result, attempt)
                
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
                        self._add_final_notes(best_result, attempt, "user_stopped")
                        return best_result
                    elif choice == "3":
                        print("\n" + "="*50)
                        print("📋 CURRENT DETECTION DETAILS:")
                        print("="*50)
                        print(self.get_product_summary(result))
                        print("\nPress ENTER to continue or type 'stop' to use this result...")
                        continue_choice = input().strip().lower()
                        if continue_choice == 'stop':
                            self._add_final_notes(result, attempt, "user_stopped_after_review")
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
            self._add_final_notes(best_result, max_attempts, "max_attempts_reached")
            return best_result
        
        return {"error": "All attempts failed with no usable results", "products": []}
    
    def _show_attempt_summary(self, result: Dict, attempt: int) -> None:
        """Show a brief summary of the current attempt's results."""
        if "error" in result:
            print(f"❌ Attempt {attempt}: Error occurred")
            return
        
        products = result.get("products", [])
        if products:
            product_count = len(products)
            main_product = products[0]
            confidence = main_product.get("confidence", "Unknown")
            name = main_product.get("name", "Unknown")
            
            print(f"📊 Attempt {attempt}: Found {product_count} product(s)")
            print(f"   Main product: {name}")
            print(f"   Confidence: {confidence}")
        else:
            print(f"📊 Attempt {attempt}: No products detected")
        
        detection_status = result.get("detection_status", "success")
        if detection_status == "needs_repositioning":
            print(f"   Status: Repositioning recommended")
        else:
            print(f"   Status: Detection successful")
    
    def _add_final_notes(self, result: Dict, total_attempts: int, stop_reason: str) -> None:
        """Add final notes to the result about the detection process."""
        if "detection_notes" not in result:
            result["detection_notes"] = ""
        
        final_note = f" | Final result after {total_attempts} attempt(s). Stop reason: {stop_reason}."
        result["detection_notes"] += final_note
        
        result["detection_summary"] = {
            "total_attempts": total_attempts,
            "stop_reason": stop_reason,
            "final_status": "completed"
        }
    
    def analyze_image(self, image_path: str, is_from_camera: bool = False, capture_info: Dict = None) -> Dict:
        """
        Analyze an image for exact product details with repositioning guidance.
        
        Args:
            image_path: Path to image file
            is_from_camera: Whether image was captured from camera
            capture_info: Camera capture metadata
            
        Returns:
            Dictionary with product detection results
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Streamlined prompt for exact product identification
        prompt = """
        EXACT PRODUCT IDENTIFICATION AI - Return ONLY valid JSON.

        REQUIREMENTS:
        1. Identify EXACT products (not generic categories)
        2. Use "N/A" for undetectable fields
        3. Request repositioning if details unclear
        4. Strict JSON format only

        {
          "detection_status": "success" | "needs_repositioning",
          "repositioning_request": {
            "needed": true | false,
            "instructions": "Specific repositioning instructions OR N/A",
            "reason": "Why repositioning needed OR N/A"
          },
          "products": [
            {
              "name": "EXACT product name OR N/A",
              "brand": "Brand name OR N/A",
              "version": "Version/model/size OR N/A",
              "category": "Category OR N/A",
              "description": "Detailed description OR N/A",
              "price": "Price OR N/A",
              "barcode": "Barcode OR N/A",
              "ingredients": "Ingredients OR N/A",
              "nutritional_info": "Nutrition info OR N/A",
              "size": "Size/weight OR N/A",
              "color": "Color OR N/A",
              "material": "Material OR N/A",
              "country_of_origin": "Origin OR N/A",
              "expiry_date": "Expiry OR N/A",
              "confidence": "High | Medium | Low",
              "identification_certainty": "Percentage OR N/A"
            }
          ],
          "image_quality": "Quality assessment",
          "visibility_issues": ["Issues or empty array"],
          "detection_notes": "Additional notes"
        }

        EXAMPLES - GOOD: "Coca-Cola Classic 12 fl oz can", "iPhone 15 Pro Max 256GB"
        EXAMPLES - BAD: "soda", "phone", "cookies"

        If unclear: Set "needs_repositioning" with specific instructions like:
        - "Rotate to show front label clearly"
        - "Hold closer to read text"
        - "Improve lighting"
        """
        
        try:
            image = Image.open(image_path)
            response = self.client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=[prompt, image]
            )
            
            # Parse and validate JSON response
            response_text = response.text.strip()
            if response_text.startswith("```"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(response_text)
            
            # Validate and fill missing fields
            self._validate_result(result)
            
            # Add capture info if from camera
            if is_from_camera and capture_info:
                result["capture_info"] = capture_info
            
            return result
            
        except json.JSONDecodeError as e:
            return self._create_error_result(f"JSON parsing failed: {str(e)}", response.text)
        except Exception as e:
            return self._create_error_result(f"Processing error: {str(e)}")
    
    def _validate_result(self, result: Dict) -> None:
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
    
    def _create_error_result(self, error_msg: str, raw_response: str = "") -> Dict:
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
    

    
    def get_product_summary(self, detection_result: Dict) -> str:
        """
        Get a human-readable summary of detected products with repositioning info.
        
        Args:
            detection_result: Result from detect_product_details
            
        Returns:
            Formatted string summary
        """
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


# Convenience function for direct image analysis
def analyze_product_image(image_path: str) -> Dict:
    """Analyze a single product image for exact details."""
    return ProductDetector().analyze_image(image_path)


def main():
    """Main function to run the interactive product detection system."""
    try:
        detector = ProductDetector()
        
        print("="*60)
        print("🎯 PRECISION PRODUCT DETECTION SYSTEM")
        print("="*60)
        print("This AI identifies EXACT products - not generic categories!")
        print("Features:")
        print("• Detects specific product names, brands, and versions")
        print("• Guides you to reposition products for better accuracy")
        print("• Up to 5 attempts for perfect identification")
        print("• Real-time feedback and instructions")
        print("• Strict JSON format with N/A for undetectable fields")
        print()
        print("Examples of what this detects:")
        print("✅ 'Coca-Cola Classic 12 fl oz can' (not just 'soda')")
        print("✅ 'iPhone 15 Pro Max 256GB Natural Titanium' (not just 'phone')")  
        print("✅ 'Oreo Original Chocolate Sandwich Cookies 14.3 oz' (not just 'cookies')")
        print()
        print("Choose your detection mode:")
        print("1. Interactive Detection (recommended) - with repositioning guidance")
        print("2. Single Capture - one attempt only")
        print("3. Quit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '3':
            print("Exiting...")
            return
        elif choice == '1':
            # Interactive detection with repositioning
            result = detector.detect_with_camera(max_attempts=5)
        elif choice == '2':
            # Single capture mode
            print("\n📸 SINGLE CAPTURE MODE")
            print("Make sure your product is clearly positioned!")
            print("Press ENTER to start or 'q' to quit...")
            
            if input().strip().lower() == 'q':
                return
                
            result = detector.detect_with_camera(max_attempts=1)
        else:
            print("Invalid choice. Using interactive mode...")
            result = detector.detect_with_camera(max_attempts=5)
        
        # Display results
        print("\n" + "="*60)
        print("🎯 FINAL DETECTION RESULTS")
        print("="*60)
        
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
            print(detector.get_product_summary(result))
            
            # Check for successful exact identification
            products = result.get("products", [])
            if products:
                exact_products = [p for p in products if p.get("confidence") in ["High", "Medium"]]
                if exact_products:
                    print(f"✅ SUCCESS: {len(exact_products)} exact product(s) identified!")
                else:
                    print("⚠️ Products detected but with low confidence.")
            
            # Offer detailed JSON view
            print("\n" + "="*40)
            print("Would you like to see the complete technical details? (y/n)")
            show_json = input().strip().lower()
            if show_json in ['y', 'yes']:
                print("\n" + "="*60)
                print("📋 COMPLETE TECHNICAL DETAILS:")
                print("="*60)
                print(json.dumps(result, indent=2))
        
        # Option to detect another product
        print("\n" + "="*60)
        print("🔄 Would you like to detect another product? (y/n)")
        another = input().strip().lower()
        
        if another in ['y', 'yes']:
            print("\n🎯 DETECTING ANOTHER PRODUCT...")
            result2 = detector.detect_with_camera(max_attempts=5)
            print("\n" + "="*60)
            print("🎯 SECOND PRODUCT RESULTS:")
            print("="*60)
            print(detector.get_product_summary(result2))
        
        print("\n✨ Thank you for using Precision Product Detection!")
        
    except KeyboardInterrupt:
        print("\n\nCapture interrupted by user. Cleaning up...")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your camera is connected and not being used by another app")
        print("2. Check that you have the required dependencies installed:")
        print("   pip install google-genai pillow opencv-python python-dotenv")
        print("3. Ensure your GEMINI_API_KEY is set in your .env file")
        print("\nAlternative usage (with existing image file):")
        print('detector = ProductDetector()')
        print('result = detector.analyze_image("path/to/product/image.jpg")')
        print('print(detector.get_product_summary(result))')


if __name__ == "__main__":
    main()
