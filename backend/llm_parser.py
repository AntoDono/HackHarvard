import json
import re
from typing import List, Dict, Any, Union


def parse_json_list(text: str) -> List[str]:
    """
    Parse a JSON list from LLM response text.
    Handles both ```json code blocks and plain JSON.
    
    Args:
        text: The response text containing a JSON list
        
    Returns:
        List[str]: Parsed list of strings
        
    Raises:
        ValueError: If no valid JSON list is found
    """
    # First try to find ```json code block
    json_pattern = r'```json\s*\n(.*?)\n```'
    match = re.search(json_pattern, text, re.DOTALL)
    
    if match:
        json_text = match.group(1).strip()
    else:
        # Look for array pattern in the text
        array_pattern = r'\[(.*?)\]'
        match = re.search(array_pattern, text, re.DOTALL)
        if match:
            json_text = f"[{match.group(1)}]"
        else:
            # Try to find any JSON array in the text
            lines = text.strip().split('\n')
            json_text = None
            for line in lines:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    json_text = line
                    break
                elif line.startswith('['):
                    # Multi-line array
                    start_idx = text.find('[')
                    end_idx = text.rfind(']')
                    if start_idx != -1 and end_idx != -1:
                        json_text = text[start_idx:end_idx + 1]
                        break
    
    if not json_text:
        raise ValueError("No JSON list found in the text")
    
    try:
        parsed = json.loads(json_text)
        if isinstance(parsed, list):
            return parsed
        else:
            raise ValueError("Parsed JSON is not a list")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")


def parse_json_object(text: str) -> Dict[str, Any]:
    """
    Parse a JSON object from LLM response text.
    Handles both ```json code blocks and plain JSON.
    
    Args:
        text: The response text containing a JSON object
        
    Returns:
        Dict[str, Any]: Parsed JSON object
        
    Raises:
        ValueError: If no valid JSON object is found
    """
    # First try to find ```json code block
    print(text)
    json_pattern = r'```json\s*\n(.*?)\n```'
    match = re.search(json_pattern, text, re.DOTALL)
    
    if match:
        json_text = match.group(1).strip()
    else:
        # Look for object pattern in the text
        object_pattern = r'\{(.*?)\}'
        match = re.search(object_pattern, text, re.DOTALL)
        if match:
            json_text = f"{{{match.group(1)}}}"
        else:
            # Try to find any JSON object in the text
            lines = text.strip().split('\n')
            json_text = None
            for line in lines:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    json_text = line
                    break
                elif line.startswith('{'):
                    # Multi-line object
                    start_idx = text.find('{')
                    end_idx = text.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        json_text = text[start_idx:end_idx + 1]
                        break
    
    if not json_text:
        raise ValueError("No JSON object found in the text")
    
    try:
        parsed = json.loads(json_text)
        if isinstance(parsed, dict):
            return parsed
        else:
            raise ValueError("Parsed JSON is not an object")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_list_text = '''
    Here are the criteria:
    ```json
    [
        "Check the serial number",
        "Verify the logo quality",
        "Inspect the stitching",
        "Check the materials",
        "Verify the packaging"
    ]
    ```
    '''
    
    test_object_text = '''
    Here's the result:
    ```json
    {
        "status": "authentic",
        "confidence": 0.95,
        "details": ["serial_valid", "logo_quality_good"]
    }
    ```
    '''
    
    test_plain_list = '''
    The criteria are:
    ["First item", "Second item", "Third item"]
    '''
    
    test_plain_object = '''
    Result: {"status": "fake", "confidence": 0.8}
    '''
    
    try:
        print("Testing parse_json_list:")
        print(parse_json_list(test_list_text))
        print(parse_json_list(test_plain_list))
        
        print("\nTesting parse_json_object:")
        print(parse_json_object(test_object_text))
        print(parse_json_object(test_plain_object))
    except Exception as e:
        print(f"Error: {e}")
