import json
import re

def clean_json_logic(response_text: str) -> str:
    # Robust stripping
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

# Test cases
test_responses = [
    """<think>
I should return a JSON object with full_name.
</think>
{
  "full_name": "John Doe"
}""",
    """Here is the result:
{
  "full_name": "Jane Smith"
}
Hope this helps!""",
    """```json
{
  "full_name": "Alice"
}
```""",
    """[
  {"id": "q1", "question": "What is your name?"}
]""",
    """<think>Thinking...</think> [
  {"id": "q2", "question": "Age?"}
]"""
]

for i, resp in enumerate(test_responses):
    cleaned = clean_json_logic(resp)
    print(f"--- Test {i+1} ---")
    print(f"Original: {resp.replace('\\n', ' ')}")
    print(f"Cleaned: {cleaned}")
    try:
        json.loads(cleaned)
        print("Status: SUCCESS")
    except Exception as e:
        print(f"Status: FAILED - {e}")
