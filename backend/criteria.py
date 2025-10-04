import os
import sqlite3
import json
import numpy as np
from google import genai
from dotenv import load_dotenv
from prompts.criteria import get_criteria_prompt
from llm_parser import parse_json_object
from sentence_transformers import SentenceTransformer
import time

load_dotenv()

# Simple cache database
CACHE_DB = "criteria_cache.db"
SIMILARITY_THRESHOLD = 0.9

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def init_cache():
    """Initialize the cache database."""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS criteria_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            criteria_data TEXT NOT NULL,
            embedding BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def cache_criteria(item: str, criteria_data: dict):
    """Store criteria data (with locations) in cache with embedding."""
    # Generate embedding for the item
    embedding = model.encode(item)
    
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO criteria_cache (item, criteria_data, embedding)
        VALUES (?, ?, ?)
    ''', (item, json.dumps(criteria_data), embedding.tobytes()))
    conn.commit()
    conn.close()

def get_cached_criteria(item: str):
    """Get cached criteria using embedding similarity."""
    # Generate embedding for the query item
    query_embedding = model.encode(item)
    
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT item, criteria_data, embedding FROM criteria_cache')
    rows = cursor.fetchall()
    conn.close()
    
    best_match = None
    best_similarity = 0.0
    
    for cached_item, criteria_json, embedding_bytes in rows:
        cached_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
        
        # Calculate cosine similarity
        similarity = np.dot(query_embedding, cached_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(cached_embedding)
        )
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = criteria_json
    
    if best_similarity >= SIMILARITY_THRESHOLD:
        print(f"Found similar item with {best_similarity:.2f} similarity")
        return json.loads(best_match)
    
    return None

def search_online_criteria(item: str, max_retries: int = 3):
    """Use Gemini Flash Lite with Google Search to find authentic criteria online."""
    from google.genai import types
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    client = genai.Client(api_key=api_key)
    
    prompt = get_criteria_prompt(item)
    
    # Configure with Google Search tool
    tools = [
        types.Tool(googleSearch=types.GoogleSearch())
    ]
    
    # Configure generation with tools
    generate_content_config = types.GenerateContentConfig(
        tools=tools,
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        )
    )
    
    # Create content
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    
    # Retry logic for JSON parsing errors
    last_error = None
    for attempt in range(max_retries):
        try:
            # Call model with search capabilities
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=contents,
                config=generate_content_config
            )
            
            content = response.text
            
            # Parse JSON object with criteria and location_angle
            criteria_data = parse_json_object(content)
            
            # Cache the results
            cache_criteria(item, criteria_data)
            
            return criteria_data
            
        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            print(f"❌ Attempt {attempt + 1}/{max_retries} failed: Invalid JSON format - {str(e)}")
            if attempt < max_retries - 1:
                print(f"🔄 Retrying...")
                time.sleep(1)  # Brief pause before retry
            else:
                print(f"❌ All {max_retries} attempts failed")
                raise Exception(f"Failed to get valid criteria after {max_retries} attempts: {str(last_error)}")

def criteria(item: str):
    """
    Get authentication criteria for an item with detailed location info and backups.
    First checks cache, then uses Gemini Flash Lite for online search.
    
    Args:
        item: The name/type of item to check
    
    Returns:
        dict: {
            "criteria": List[str],  # Simplified list for backward compatibility
            "location_angle": List[str],  # Simplified list for backward compatibility
            "detailed_criteria": List[dict]  # Full detailed criteria with backups
        }
    """
    # Initialize cache if needed
    init_cache()
    
    # Check cache first
    cached_criteria = get_cached_criteria(item)
    if cached_criteria:
        print(f"Using cached criteria for {item}")
        return cached_criteria
    
    # If not cached, search online
    print(f"Searching online for {item}")
    detailed_data = search_online_criteria(item)
    
    # Transform detailed format to include backward-compatible simple lists
    if "criteria" in detailed_data and isinstance(detailed_data["criteria"], list):
        if len(detailed_data["criteria"]) > 0 and isinstance(detailed_data["criteria"][0], dict):
            # New detailed format - extract simple lists for backward compatibility
            simple_criteria = []
            simple_locations = []
            
            for criterion in detailed_data["criteria"]:
                # Primary feature as the main criterion
                simple_criteria.append(criterion.get("primary_feature", ""))
                # Primary location + how to photograph
                location_str = f"{criterion.get('primary_location', '')} - {criterion.get('how_to_photograph', '')}"
                simple_locations.append(location_str)
            
            result = {
                "criteria": simple_criteria,
                "location_angle": simple_locations,
                "detailed_criteria": detailed_data["criteria"]
            }
            
            # Cache the full result
            cache_criteria(item, result)
            return result
    
    # Fallback: old format or unexpected format
    return detailed_data


if __name__ == "__main__":
    item_name = "LV Baby Blue Card Holder"
    time_now = time.time()
    print(f"Authentication criteria for {item_name}:\n")
    
    authentication_criteria = criteria(item_name)
    
    # Show detailed criteria if available
    if "detailed_criteria" in authentication_criteria:
        print(f"\nDetailed Criteria ({len(authentication_criteria.get('detailed_criteria', []))} items):")
        for i, criterion in enumerate(authentication_criteria.get('detailed_criteria', []), 1):
            print(f"\n{i}. PRIMARY FEATURE:")
            print(f"   {criterion.get('primary_feature', 'N/A')}")
            print(f"   📍 Location: {criterion.get('primary_location', 'N/A')}")
            print(f"   ❓ Why Important: {criterion.get('why_important', 'N/A')}")
            print(f"   📸 How to Photograph: {criterion.get('how_to_photograph', 'N/A')}")
            print(f"\n   BACKUP OPTION:")
            print(f"   {criterion.get('backup_feature', 'N/A')}")
            print(f"   📍 Backup Location: {criterion.get('backup_location', 'N/A')}")
            print(f"   📸 Backup Photography: {criterion.get('backup_how_to_photograph', 'N/A')}")
    else:
        # Fallback to simple format
        print(f"\nCriteria ({len(authentication_criteria.get('criteria', []))} items):")
        for i, (criterion, location) in enumerate(zip(
            authentication_criteria.get('criteria', []),
            authentication_criteria.get('location_angle', [])
        ), 1):
            print(f"{i}. {criterion}")
            print(f"   📍 {location}")
    
    time_elapsed = time.time() - time_now
    print(f"\nTime elapsed: {time_elapsed} seconds")
