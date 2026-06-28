import os
import requests

def translate_text(text, target_lang):
    """
    Translates text to target_lang using LibreTranslate.
    Supported languages: 'ta' (Tamil), 'hi' (Hindi), 'te' (Telugu), 'en' (English).
    If target_lang is 'en', returns text directly.
    """
    if not target_lang or target_lang == 'en':
        return text

    # Set up LibreTranslate endpoint
    # Defaulting to a public instance or env variable
    url = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.de")
    api_key = os.getenv("LIBRETRANSLATE_KEY", "")
    
    # Clean language code
    target_lang = target_lang.lower().strip()
    
    try:
        payload = {
            "q": text,
            "source": "en",
            "target": target_lang,
            "format": "text"
        }
        if api_key:
            payload["api_key"] = api_key
            
        headers = { "Content-Type": "application/json" }
        
        # Post request to LibreTranslate
        response = requests.post(f"{url}/translate", json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("translatedText", text)
        else:
            print(f"LibreTranslate returned status code {response.status_code}: {response.text}")
            # Fallback to local translation notice
            return f"{text}\n\n*(Translation to {target_lang.upper()} is temporarily unavailable. Displayed in English)*"
    except Exception as e:
        print(f"LibreTranslate Error: {str(e)}")
        # Fallback to returning original English text
        return f"{text}\n\n*(Translation service connection failed. Displayed in English)*"
