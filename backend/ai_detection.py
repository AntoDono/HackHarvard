
    # this example uses requests
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def detect_deepfake(image_url: str) -> float:
    params = {
    'url': image_url,
    'models': 'genai',
    'api_user': os.environ.get("SIGHTENGINE_API_USER"),
    'api_secret': os.environ.get("SIGHTENGINE_API_SECRET")
    }
    r = requests.get('https://api.sightengine.com/1.0/check.json', params=params)

    output = json.loads(r.text)

    if output.get('status') == 'success':
        return output.get('type').get('ai_generated')
    else:
        return None
