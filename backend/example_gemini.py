# To run this code you need to install the following dependencies:
# pip install google-genai pillow

import os
from pathlib import Path
from google import genai
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()

def analyze_image(image_path: str, prompt: str = "What's in this image?"):
    """
    Simple example: Send an image and text prompt to Gemini, get a text response.
    
    Args:
        image_path: Path to the image file
        prompt: Text prompt to send with the image
    """
    # Initialize the Gemini client
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )
    
    # Open and upload the image
    image = Image.open(image_path)
    
    # Generate content with the image and text
    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=[prompt, image]
    )
    
    return response.text

if __name__ == "__main__":
    # Example usage
    # Replace 'path/to/your/image.jpg' with your actual image path
    image_path = "./test_materials/dog.png"
    
    if Path(image_path).exists():
        result = analyze_image(image_path, "Describe this image in detail.")
        print(result)
    else:
        print(f"Please provide a valid image path. Current path '{image_path}' not found.")
        print("\nExample usage:")
        print('result = analyze_image("your_image.jpg", "What objects are in this image?")')
        print('print(result)')
