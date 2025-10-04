import os
import sqlite3
import json
import numpy as np
from groq import Groq
from dotenv import load_dotenv
from prompts.criteria import get_criteria_prompt
from llm_parser import parse_json_list
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
            criteria TEXT NOT NULL,
            embedding BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def cache_criteria(item: str, criteria: list):
    """Store criteria in cache with embedding."""
    # Generate embedding for the item
    embedding = model.encode(item)
    
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO criteria_cache (item, criteria, embedding)
        VALUES (?, ?, ?)
    ''', (item, json.dumps(criteria), embedding.tobytes()))
    conn.commit()
    conn.close()

def get_cached_criteria(item: str):
    """Get cached criteria using embedding similarity."""
    # Generate embedding for the query item
    query_embedding = model.encode(item)
    
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT item, criteria, embedding FROM criteria_cache')
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
    """Use Groq Compound to search online for criteria."""
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    prompt = get_criteria_prompt(item)

    response = client.chat.completions.create(
        model="groq/compound",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    
    content = response.choices[0].message.content
    
    if hasattr(response.choices[0].message, 'executed_tools'):
        print("Web search tool used.")
    
    criteria_list = parse_json_list(content)
    
    # Cache the results
    cache_criteria(item, criteria_list)
    
    return criteria_list

def criteria(item: str):
    """
    Get authentication criteria for an item.
    First checks cache, then uses Groq Compound for online search.
    
    Args:
        item: The name/type of item to check
    
    Returns:
        list: A list of 5 specific details to look for when identifying counterfeits
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
    
    for i, criterion in enumerate(authentication_criteria, 1):
        print(f"{i}. {criterion}")

    time_elapsed = time.time() - time_now
    print(f"Time elapsed: {time_elapsed} seconds")

