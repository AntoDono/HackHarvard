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

def search_online_criteria(item: str):
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
    
    # Call model with search capabilities
    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=contents,
        config=generate_content_config
    )
    
    content = response.text
    
    # Parse JSON object with criteria and location_angle
    criteria_data = parse_json_object(content)
    
    # Cache the results
    cache_criteria(item, criteria_data)
    
    return criteria_data

def criteria(item: str):
    """
    Get authentication criteria for an item.
    First checks cache, then uses Gemini Flash Lite for online search.
    
    Args:
        item: The name/type of item to check
    
    Returns:
        dict: {
            "criteria": List[str],
            "location_angle": List[str]
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
    return search_online_criteria(item)


if __name__ == "__main__":
    item_name = "LV Baby Blue Card Holder"
    time_now = time.time()
    print(f"Authentication criteria for {item_name}:\n")
    
    authentication_criteria = criteria(item_name)
    
    print(f"\nCriteria ({len(authentication_criteria.get('criteria', []))} items):")
    for i, (criterion, location) in enumerate(zip(
        authentication_criteria.get('criteria', []),
        authentication_criteria.get('location_angle', [])
    ), 1):
        print(f"{i}. {criterion}")
        print(f"   📍 {location}")
    
    time_elapsed = time.time() - time_now
    print(f"\nTime elapsed: {time_elapsed} seconds")
