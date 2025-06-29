from translate import Translator

def translate_titles(titles, src='es', dest='en'):
    translator = Translator(from_lang=src, to_lang=dest)
    translated = []
    for title in titles:
        try:
            translated_text = translator.translate(title)
            translated.append(translated_text)
        except Exception as e:
            print(f"Translation failed for '{title}': {e}")
            translated.append(title)  # fallback to original if error
    return translated
