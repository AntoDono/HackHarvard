import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid
import mimetypes

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "image")  # Default bucket name

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_image_to_supabase(
    local_image_path: str,
    folder: Optional[str] = None,
    custom_filename: Optional[str] = None
) -> str:
    """
    Upload an image from local path to Supabase storage and return the public URL.
    
    Args:
        local_image_path (str): Path to the local image file
        folder (str, optional): Folder path in the bucket (e.g., 'products', 'criteria')
        custom_filename (str, optional): Custom filename. If not provided, uses original filename with UUID
        
    Returns:
        str: Public URL of the uploaded image
        
    Raises:
        FileNotFoundError: If the local image file doesn't exist
        Exception: If upload fails
        
    Example:
        >>> url = upload_image_to_supabase('/path/to/image.jpg', folder='products')
        >>> print(url)
        https://xxxxx.supabase.co/storage/v1/object/public/image/products/abc-123.jpg
    """
    # Validate file exists
    image_path = Path(local_image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {local_image_path}")
    
    if not image_path.is_file():
        raise ValueError(f"Path is not a file: {local_image_path}")
    
    # Get file extension and mime type
    file_extension = image_path.suffix.lower()
    mime_type, _ = mimetypes.guess_type(local_image_path)
    
    if not mime_type or not mime_type.startswith('image/'):
        raise ValueError(f"File is not a valid image: {local_image_path}")
    
    # Generate filename
    if custom_filename:
        filename = custom_filename
        if not filename.endswith(file_extension):
            filename += file_extension
    else:
        # Create unique filename: original-name_uuid.ext
        unique_id = str(uuid.uuid4())[:8]
        original_name = image_path.stem
        filename = f"{original_name}_{unique_id}{file_extension}"
    
    # Build storage path
    if folder:
        storage_path = f"{folder.strip('/')}/{filename}"
    else:
        storage_path = filename
    
    # Read image file
    with open(local_image_path, 'rb') as f:
        image_data = f.read()
    
    # Upload to Supabase
    try:
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=storage_path,
            file=image_data,
            file_options={"content-type": mime_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
        
        return public_url
        
    except Exception as e:
        # If file already exists, you might want to either overwrite or return existing URL
        if "already exists" in str(e).lower():
            # Return the public URL of the existing file
            public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
            return public_url
        else:
            raise Exception(f"Failed to upload image to Supabase: {str(e)}")


def delete_image_from_supabase(storage_path: str) -> bool:
    """
    Delete an image from Supabase storage.
    
    Args:
        storage_path (str): Path of the file in the bucket (e.g., 'products/image.jpg')
        
    Returns:
        bool: True if deletion was successful
        
    Example:
        >>> success = delete_image_from_supabase('products/abc-123.jpg')
    """
    try:
        supabase.storage.from_(SUPABASE_BUCKET).remove([storage_path])
        return True
    except Exception as e:
        raise Exception(f"Failed to delete image from Supabase: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Example: Upload an image
    try:
        # Replace with your actual image path
        test_image = "test_materials/dog.png"
        
        if os.path.exists(test_image):
            url = upload_image_to_supabase(
                local_image_path=test_image,
                folder="test",
                custom_filename=None  # Will auto-generate unique filename
            )
            print(f"✓ Image uploaded successfully!")
            print(f"Public URL: {url}")
        else:
            print(f"Test image not found: {test_image}")
            print("Please provide a valid image path to test the upload function")
            
    except Exception as e:
        print(f"✗ Upload failed: {e}")

if __name__ == "__main__":
    test_image = "test_materials/dog.png"
    url = upload_image_to_supabase(
        local_image_path="./test_materials/dog.png",
    )
    print(f"Public URL: {url}")