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
        
        # Comprehensive prompt for product detection
        prompt = """
        Analyze this image and extract detailed product information. Please provide the response in JSON format with the following structure:
        
        {
          "products": [
            {
              "name": "Product name",
              "brand": "Brand name",
              "version": "Version/model number if visible",
              "category": "Product category",
              "description": "Detailed description",
              "price": "Price if visible (null if not)",
              "barcode": "Barcode number if visible (null if not)",
              "ingredients": "List of ingredients if visible (null if not)",
              "nutritional_info": "Nutritional information if visible (null if not)",
              "size": "Size/dimensions if visible",
              "color": "Primary color(s)",
              "material": "Material if identifiable",
              "country_of_origin": "Country of origin if visible",
              "expiry_date": "Expiry date if visible (null if not)",
              "confidence": "High/Medium/Low - confidence level of detection"
            }
          ],
          "image_quality": "Assessment of image quality for detection",
          "detection_notes": "Any additional notes about the detection process"
        }
        
        If multiple products are visible, include them all in the products array. If certain information is not visible or identifiable, use null for those fields. Be as accurate and detailed as possible.
        """
        
        try:
            # Open and process the image
            image = Image.open(image_path)
            
            # Generate content with the image and prompt
            response = self.client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=[prompt, image]
            )
            
            # Try to parse the JSON response
            try:
                result = json.loads(response.text)
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw text
                return {
                    "error": "Failed to parse JSON response",
                    "raw_response": response.text,
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
        Get a human-readable summary of detected products.
        
        Args:
            detection_result: Result from detect_product_details
            
        Returns:
            Formatted string summary
        """
        if "error" in detection_result:
            return f"Error: {detection_result['error']}"
        
        if not detection_result.get("products"):
            return "No products detected in the image."
        
        summary = []
        summary.append(f"Detected {len(detection_result['products'])} product(s):\n")
        
        for i, product in enumerate(detection_result["products"], 1):
            summary.append(f"{i}. {product.get('name', 'Unknown Product')}")
            if product.get('brand'):
                summary.append(f"   Brand: {product['brand']}")
            if product.get('version'):
                summary.append(f"   Version: {product['version']}")
            if product.get('category'):
                summary.append(f"   Category: {product['category']}")
            if product.get('price'):
                summary.append(f"   Price: {product['price']}")
            summary.append(f"   Confidence: {product.get('confidence', 'Unknown')}")
            summary.append("")
        
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
    # Example usage with camera capture
    try:
        detector = ProductDetector()
        
        print("="*60)
        print("LIVE PRODUCT DETECTION WITH CAMERA")
        print("="*60)
        print("This will:")
        print("1. Open your camera")
        print("2. Show a 5-second countdown")
        print("3. Capture an image of your product")
        print("4. Analyze the product details using AI")
        print("\nMake sure you have a product ready to scan!")
        print("Press ENTER to start or 'q' to quit...")
        
        user_input = input().strip().lower()
        if user_input == 'q':
            print("Exiting...")
            exit()
        
        # Capture and analyze product
        result = detector.capture_and_detect(countdown_seconds=5, save_path="captured_product.jpg")
        
        print("\n" + "="*60)
        print("PRODUCT DETECTION RESULTS")
        print("="*60)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            if "raw_response" in result:
                print(f"Raw response: {result['raw_response']}")
        else:
            # Print capture info
            if "capture_info" in result:
                capture_info = result["capture_info"]
                print(f"📸 Image captured at: {capture_info['capture_time']}")
                print(f"💾 Saved to: {capture_info['image_path']}")
                print()
            
            # Print product summary
            print("🔍 DETECTED PRODUCTS:")
            print(detector.get_product_summary(result))
            
            # Ask if user wants full JSON details
            print("Would you like to see the full detailed JSON response? (y/n)")
            show_json = input().strip().lower()
            if show_json in ['y', 'yes']:
                print("\n" + "="*60)
                print("FULL JSON RESPONSE:")
                print("="*60)
                print(json.dumps(result, indent=2))
        
        # Option for another capture
        print("\n" + "="*60)
        print("Would you like to capture another product? (y/n)")
        another = input().strip().lower()
        
        if another in ['y', 'yes']:
            print("Starting another capture...")
            result2 = detector.capture_and_detect(countdown_seconds=5, save_path="captured_product_2.jpg")
            print("\n🔍 SECOND CAPTURE RESULTS:")
            if "error" not in result2:
                print(detector.get_product_summary(result2))
            else:
                print(f"❌ Error: {result2['error']}")
        
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
