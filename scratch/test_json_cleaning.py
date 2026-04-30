import re
import json

def clean_json_logic(response_text):
    clean_text = response_text.strip()
    
    # 1. Remove <think> tags (reasoning)
    clean_text = re.sub(r'<think>.*?</think>', '', clean_text, flags=re.DOTALL).strip()

    # 2. Handle markdown fences more aggressively
    if "```" in clean_text:
        # Look for content between fences
        if "```json" in clean_text.lower():
            parts = clean_text.split("```")
            for part in parts:
                part = part.strip()
                if part.lower().startswith("json"):
                    clean_text = part[4:].strip()
                    break
        else:
            # General markdown fence
            parts = clean_text.split("```")
            for part in parts:
                part = part.strip()
                if (part.startswith("{") and part.endswith("}")) or (part.startswith("[") and part.endswith("]")):
                    clean_text = part
                    break
    
    # 3. Final clean-up of common hallucinations
    clean_text = clean_text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    
    # 4. Find the actual start of JSON (either { or [)
    start_obj = clean_text.find("{")
    start_arr = clean_text.find("[")
    
    start_idx = -1
    if start_obj != -1 and start_arr != -1:
        start_idx = min(start_obj, start_arr)
    elif start_obj != -1:
        start_idx = start_obj
    elif start_arr != -1:
        start_idx = start_arr

    if start_idx != -1:
        # Found a potential JSON start
        if start_obj == start_idx:
            # Object
            end_idx = clean_text.rfind("}")
            if end_idx != -1:
                clean_text = clean_text[start_idx : end_idx + 1]
        else:
            # Array
            end_idx = clean_text.rfind("]")
            if end_idx != -1:
                clean_text = clean_text[start_idx : end_idx + 1]
    
    return clean_text

test_cases = [
    "<think>Reasoning here</think>{\"key\": \"value\"}",
    "```json\n{\"key\": \"value\"}\n```",
    "Sure! Here is the JSON: ```\n{\"key\": \"value\"}\n```",
    "<think>Empty response</think>",
    "Just text, no JSON",
    "Nested JSON: Here is one: {\"a\": 1} and another {\"b\": 2}",
]

for i, tc in enumerate(test_cases):
    cleaned = clean_json_logic(tc)
    print(f"Test Case {i}:")
    print(f"  Input: {tc!r}")
    print(f"  Cleaned: {cleaned!r}")
    try:
        if cleaned:
            json.loads(cleaned)
            print("  Status: VALID JSON")
        else:
            print("  Status: EMPTY STRING")
    except Exception as e:
        print(f"  Status: INVALID JSON - {e}")
    print("-" * 20)
