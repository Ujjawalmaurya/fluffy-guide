import re
import json
from loguru import logger

def clean_and_extract_json_text(response_text: str) -> str:
    """
    Cleans response text, finds JSON boundaries, and attempts to close open braces/brackets.
    """
    text = response_text.strip()
    
    # Remove common markdown clutter
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    
    # Find the boundaries of the JSON object/array
    start_idx = text.find("{")
    if start_idx == -1: 
        start_idx = text.find("[")
    
    if start_idx != -1:
        # Truncate text before JSON
        text = text[start_idx:]
        
        # Try to find the last closing brace/bracket
        end_idx = text.rfind("}")
        if end_idx == -1: 
            end_idx = text.rfind("]")
        
        if end_idx != -1:
            text = text[:end_idx+1]
        else:
            # HEALING: Truncated JSON? Try to close it.
            open_braces = text.count("{") - text.count("}")
            if open_braces > 0:
                text += "}" * open_braces
            open_brackets = text.count("[") - text.count("]")
            if open_brackets > 0:
                text += "]" * open_brackets
    return text

def parse_healed_json(text: str) -> dict:
    """
    Parses JSON with healing strategies for common LLM syntax errors.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Healing attempt: fix common typos
        # 1. Remove trailing commas in arrays/objects
        text = re.sub(r",\s*([\]\}])", r"\1", text) 
        # 2. Quote unquoted keys (simple alphanumeric)
        text = re.sub(r"([{,]\s*)([a-zA-Z0-9_]+)\s*:", r'\1"\2":', text)
        # 3. Handle single quotes as double quotes
        text = text.replace("'", '"') 
        # 4. Remove ellipsis if model truncated list
        text = text.replace("...", "")
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as final_e:
            logger.warning(f"[LLM_JSON_UTILS] JSON healing failed. Text snippet: {text[:100]}...")
            raise final_e
