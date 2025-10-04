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
    A class to detect products, brands, versions and details from images using Gemini AI.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ProductDetector with Gemini API key.
        
        Args:
            api_key: Gemini API key. If None, will try to get from environment.
        """
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
    
    def capture_and_detect(self, countdown_seconds: int = 5, save_path: str = "captured_product.jpg") -> Dict:
        """
        Capture an image with timer and immediately analyze it for products.
        
        Args:
            countdown_seconds: Number of seconds to count down before capture
            save_path: Path where to save the captured image
            
        Returns:
            Dictionary containing product detection results
        """
        try:
            # Capture the image
            image_path = self.capture_image_with_timer(countdown_seconds, save_path)
            
            # Analyze the captured image
            print("Analyzing captured image for products...")
            result = self.detect_product_details(image_path)
            
            # Add capture info to result
            result["capture_info"] = {
                "image_path": image_path,
                "capture_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "countdown_seconds": countdown_seconds
            }
            
            return result
            
        except Exception as e:
            return {
                "error": f"Error during capture and detection: {str(e)}",
                "products": []
            }
    
    def interactive_product_detection(self, max_attempts: int = 5) -> Dict:
        """
        Interactive product detection with repositioning guidance.
        
        Args:
            max_attempts: Maximum number of capture attempts
            
        Returns:
            Final detection result after repositioning attempts
        """
        print("🎯 PRECISION PRODUCT DETECTION")
        print("=" * 50)
        print("This AI will identify EXACT products, not generic categories.")
        print(f"If needed, it will guide you to reposition your product (up to {max_attempts} attempts).")
        print()
        
        for attempt in range(1, max_attempts + 1):
            print(f"📸 ATTEMPT {attempt}/{max_attempts}")
            print("-" * 30)
            
            if attempt == 1:
                print("Position your product clearly in front of the camera.")
                print("Make sure the brand name and product details are visible.")
            
            try:
                # Capture and analyze
                result = self.capture_and_detect(
                    countdown_seconds=5, 
                    save_path=f"product_attempt_{attempt}.jpg"
                )
                
                if "error" in result:
                    print(f"❌ Capture error: {result['error']}")
                    if attempt < max_attempts:
                        print("Let's try again...")
                        continue
                    else:
                        return result
                
                # Check if repositioning is needed
                detection_status = result.get("detection_status", "success")
                repositioning = result.get("repositioning_request", {})
                
                if detection_status == "needs_repositioning" and repositioning.get("needed", False):
                    print(f"🔄 REPOSITIONING NEEDED")
                    print(f"Reason: {repositioning.get('reason', 'Better view needed')}")
                    print(f"Instructions: {repositioning.get('instructions', 'Please adjust product position')}")
                    
                    if attempt < max_attempts:
                        print(f"\nLet's try again with better positioning (Attempt {attempt + 1}/{max_attempts})")
                        print("Press ENTER when you've repositioned the product...")
                        input()
                        continue
                    else:
                        print(f"\n⚠️ Maximum attempts reached. Showing best available detection...")
                        return result
                
                else:
                    # Successful detection
                    print("✅ EXACT PRODUCT IDENTIFIED!")
                    return result
                    
            except Exception as e:
                print(f"❌ Error in attempt {attempt}: {str(e)}")
                if attempt < max_attempts:
                    print("Let's try again...")
                    continue
                else:
                    return {
                        "error": f"All attempts failed. Last error: {str(e)}",
                        "products": []
                    }
        
        return {
            "error": "Maximum attempts exceeded without successful detection",
            "products": []
        }
    
    def detect_product_details(self, image_path: str) -> Dict:
        """
        Detect comprehensive product details from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing detected product information
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found at path: {image_path}")
        
        # Comprehensive prompt for product detection with specificity requirements
        prompt = """
        You are a highly precise product identification AI. Your task is to identify EXACT, SPECIFIC products - NOT generic categories.

        CRITICAL REQUIREMENTS:
        1. You MUST identify the EXACT product name, brand, and model/version
        2. NEVER give generic answers like "soda can" or "cereal box" 
        3. If you cannot see enough detail to identify the EXACT product, you MUST request repositioning
        4. Be extremely specific - for example: "Coca-Cola Classic 12 fl oz can" not just "Coca-Cola"
        5. STRICTLY FOLLOW THE JSON FORMAT - no deviations allowed
        6. Use "N/A" for any field you cannot detect or identify

        MANDATORY: Your response MUST be valid JSON format ONLY. No additional text before or after the JSON.

        Analyze this image and extract detailed product information. Provide response in EXACT JSON format:
        
        {
          "detection_status": "success" | "needs_repositioning",
          "repositioning_request": {
            "needed": true | false,
            "instructions": "Specific instructions for user to reposition product OR N/A",
            "reason": "Why repositioning is needed OR N/A"
          },
          "products": [
            {
              "name": "EXACT product name (must be specific, not generic) OR N/A",
              "brand": "Brand name OR N/A",
              "version": "Exact version/model/size OR N/A",
              "category": "Product category OR N/A",
              "description": "Detailed description with specifics OR N/A",
              "price": "Price if visible OR N/A",
              "barcode": "Barcode number if visible OR N/A",
              "ingredients": "List of ingredients if visible OR N/A",
              "nutritional_info": "Nutritional information if visible OR N/A",
              "size": "Exact size/dimensions/weight if visible OR N/A",
              "color": "Primary color(s) OR N/A",
              "material": "Material if identifiable OR N/A",
              "country_of_origin": "Country of origin if visible OR N/A",
              "expiry_date": "Expiry date if visible OR N/A",
              "confidence": "High | Medium | Low",
              "identification_certainty": "Percentage (e.g., 85%) OR N/A"
            }
          ],
          "image_quality": "Assessment of image quality for detection",
          "visibility_issues": ["List any text/labels that are unclear or need better angles, empty array if none"],
          "detection_notes": "Any additional notes about the detection process"
        }
        
        FIELD REQUIREMENTS:
        - ALL fields must be present in the JSON
        - Use "N/A" (exactly this string) for any undetectable information
        - Never use null, empty strings, or omit fields
        - Arrays can be empty [] if no items to list
        - Confidence must be exactly "High", "Medium", or "Low"
        - Detection_status must be exactly "success" or "needs_repositioning"
        
        EXAMPLES OF WHAT TO DO:
        ✅ GOOD: "Oreo Original Chocolate Sandwich Cookies 14.3 oz package"
        ✅ GOOD: "iPhone 15 Pro Max 256GB in Natural Titanium"
        ✅ GOOD: "Tide Liquid Laundry Detergent Original Scent 64 loads 92 fl oz"
        
        EXAMPLES OF WHAT NOT TO DO:
        ❌ BAD: "cookies" or "phone" or "laundry detergent"
        ❌ BAD: "chocolate cookies" or "smartphone" or "cleaning product"
        
        REPOSITIONING INSTRUCTIONS:
        If you cannot identify the EXACT product because:
        - Text is blurry or partially obscured
        - Product label is not fully visible
        - Barcode or important details are hidden
        - Lighting is poor
        - Product is at wrong angle
        
        Then set "detection_status": "needs_repositioning" and provide specific instructions like:
        - "Please rotate the product to show the front label clearly"
        - "Please hold the product closer to the camera to read the text"
        - "Please turn the product to show the ingredients/nutritional panel"
        - "Please improve lighting - the text is too dark to read"
        - "Please hold the product steadier - the image is blurry"
        
        CRITICAL: Return ONLY valid JSON. No explanatory text. No markdown formatting. Pure JSON only.
        Remember: It's better to ask for repositioning than to give a generic identification!
        """
        
        try:
            # Open and process the image
            image = Image.open(image_path)
            
            # Generate content with the image and prompt
            response = self.client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=[prompt, image]
            )
            
            # Try to parse the JSON response with enhanced error handling
            try:
                # Clean the response text to ensure pure JSON
                response_text = response.text.strip()
                
                # Remove any markdown formatting if present
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "").replace("```", "").strip()
                elif response_text.startswith("```"):
                    response_text = response_text.replace("```", "").strip()
                
                result = json.loads(response_text)
                
                # Validate required fields and add N/A if missing
                if "products" in result and result["products"]:
                    for product in result["products"]:
                        required_fields = [
                            "name", "brand", "version", "category", "description",
                            "price", "barcode", "ingredients", "nutritional_info",
                            "size", "color", "material", "country_of_origin",
                            "expiry_date", "confidence", "identification_certainty"
                        ]
                        for field in required_fields:
                            if field not in product or product[field] is None or product[field] == "":
                                product[field] = "N/A"
                
                # Ensure repositioning_request has required structure
                if "repositioning_request" not in result:
                    result["repositioning_request"] = {
                        "needed": False,
                        "instructions": "N/A",
                        "reason": "N/A"
                    }
                
                return result
                
            except json.JSONDecodeError as e:
                # Enhanced error handling for JSON parsing failures
                return {
                    "error": f"Failed to parse JSON response: {str(e)}",
                    "raw_response": response.text[:500] + "..." if len(response.text) > 500 else response.text,
                    "detection_status": "needs_repositioning",
                    "repositioning_request": {
                        "needed": True,
                        "instructions": "AI response was not in valid JSON format. Please try capturing again with better lighting and clearer product view.",
                        "reason": "JSON parsing error - response format issue"
                    },
                    "products": []
                }
                
        except Exception as e:
            return {
                "error": f"Error processing image: {str(e)}",
                "products": []
            }
    
    def detect_specific_product(self, image_path: str, product_query: str) -> Dict:
        """
        Detect specific product information based on a query.
        
        Args:
            image_path: Path to the image file
            product_query: Specific query about the product (e.g., "Is this a Coca-Cola product?")
            
        Returns:
            Dictionary containing query-specific product information
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found at path: {image_path}")
        
        prompt = f"""
        Analyze this image with focus on the following query: "{product_query}"
        
        Please provide detailed information about what you can identify in relation to this query.
        Include:
        - Product identification
        - Brand information
        - Specific details relevant to the query
        - Confidence level of your identification
        
        Format your response as a detailed analysis.
        """
        
        try:
            image = Image.open(image_path)
            
            response = self.client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=[prompt, image]
            )
            
            return {
                "query": product_query,
                "analysis": response.text,
                "image_path": image_path
            }
            
        except Exception as e:
            return {
                "error": f"Error processing specific query: {str(e)}",
                "query": product_query
            }
    
    def batch_detect_products(self, image_paths: List[str]) -> List[Dict]:
        """
        Detect products from multiple images.
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            List of dictionaries containing product information for each image
        """
        results = []
        
        for i, image_path in enumerate(image_paths):
            print(f"Processing image {i+1}/{len(image_paths)}: {Path(image_path).name}")
            
            try:
                result = self.detect_product_details(image_path)
                result["image_path"] = image_path
                result["processing_order"] = i + 1
                results.append(result)
            except Exception as e:
                results.append({
                    "error": f"Failed to process {image_path}: {str(e)}",
                    "image_path": image_path,
                    "processing_order": i + 1,
                    "products": []
                })
        
        return results
    
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


def analyze_product_image(image_path: str, query: Optional[str] = None) -> Dict:
    """
    Convenience function to analyze a single product image.
    
    Args:
        image_path: Path to the image file
        query: Optional specific query about the product
        
    Returns:
        Dictionary containing product detection results
    """
    detector = ProductDetector()
    
    if query:
        return detector.detect_specific_product(image_path, query)
    else:
        return detector.detect_product_details(image_path)


if __name__ == "__main__":
    # Example usage with interactive precision detection
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
            exit()
        elif choice == '1':
            # Interactive detection with repositioning
            result = detector.interactive_product_detection(max_attempts=5)
        elif choice == '2':
            # Single capture mode
            print("\n📸 SINGLE CAPTURE MODE")
            print("Make sure your product is clearly positioned!")
            print("Press ENTER to start capture or 'q' to quit...")
            
            user_input = input().strip().lower()
            if user_input == 'q':
                print("Exiting...")
                exit()
                
            result = detector.capture_and_detect(countdown_seconds=5, save_path="captured_product.jpg")
        else:
            print("Invalid choice. Using interactive mode...")
            result = detector.interactive_product_detection(max_attempts=5)
        
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
            result2 = detector.interactive_product_detection(max_attempts=5)
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
        print('result = detector.detect_product_details("path/to/product/image.jpg")')
        print('print(detector.get_product_summary(result))')
