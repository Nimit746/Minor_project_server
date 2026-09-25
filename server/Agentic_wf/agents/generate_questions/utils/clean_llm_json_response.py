import re

def clean_llm_json_response(response_text: str) -> str:
    """
    Robustly clean and repair LLM JSON responses to fix common issues:
    - Removes markdown fences
    - Extracts only the JSON array/object from extraneous text
    - Fixes truncated JSON
    - Removes repeated content that causes parsing failures
    """
    if not response_text:
        return ""
    
    # Initial stripping
    cleaned = response_text.strip()
    
    # Remove markdown code fences
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    # Extract JSON array (most common case for batch generation)
    start_idx = cleaned.find('[')
    end_idx = cleaned.rfind(']')
    
    if start_idx != -1 and end_idx != -1:
        cleaned = cleaned[start_idx:end_idx+1]
        # Find the last valid JSON object closing to fix truncation
        last_brace = cleaned.rfind('}')
        if last_brace != -1:
            cleaned = cleaned[:last_brace+1] + "]"
    else:
        # If no array found, try to extract a single JSON object
        obj_start = cleaned.find('{')
        obj_end = cleaned.rfind('}')
        if obj_start != -1 and obj_end != -1:
            cleaned = cleaned[obj_start:obj_end+1]
    
    # Remove any remaining non-JSON text
    cleaned = re.sub(r'Raw LLM response:.*?\[', '[', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'JSON:.*?\[', '[', cleaned, flags=re.DOTALL)
    
    return cleaned.strip()