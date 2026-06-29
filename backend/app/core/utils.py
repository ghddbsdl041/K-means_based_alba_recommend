import logging
import xmltodict
from typing import Dict, Any

logger = logging.getLogger(__name__)

def parse_xml_to_dict(xml_content: str) -> Dict[str, Any]:
    """
    Safely parse an XML string response into a clean, standard Python dictionary.
    Includes exception handling and logging for robustness.
    """
    try:
        if not xml_content or not xml_content.strip():
            return {}
        
        # xmltodict handles full XML parsing and returns clean nested dicts
        parsed_dict = xmltodict.parse(xml_content, dict_constructor=dict)
        return clean_dict_keys(parsed_dict)
    except Exception as e:
        logger.error(f"Failed to parse XML content: {e}. Content snippet: {xml_content[:500]}")
        raise ValueError(f"Error parsing XML response from Work24 API: {str(e)}")

def clean_dict_keys(data: Any) -> Any:
    """
    Recursively traverses dictionaries and lists to strip whitespace from keys 
    and values, ensuring formatting consistency.
    """
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            # Strip key and remove any '@' attributes prefix if created by xmltodict
            clean_key = k.strip()
            if clean_key.startswith("@"):
                clean_key = clean_key[1:]
            cleaned[clean_key] = clean_dict_keys(v)
        return cleaned
    elif isinstance(data, list):
        return [clean_dict_keys(item) for item in data]
    elif isinstance(data, str):
        return data.strip()
    return data
