import requests
import json

def translate_text(text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
    """
    Translates text from source language to target language using the LibreTranslate API.
    
    Args:
        text (str): The text to translate.
        source_lang (str): The source language (default: "auto" for automatic detection).
        target_lang (str): The target language (default: "en" for English).
        
    Returns:
        str: The translated text.
    """
    url = "https://libretranslate.com/translate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json().get("translatedText", "")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return ""

# Example usage
if __name__ == "__main__":
    translated_text = translate_text("Ciao!")
    print("Translated text:", translated_text)
