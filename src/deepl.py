"""Translation module — Bing > Youdao > Sogou"""
import time

def translate(text, target_lang="en", api_key=None):
    if not text or not text.strip():
        return text
    for engine in ['bing', 'youdao', 'sogou']:
        try:
            import translators as ts
            result = ts.translate_text(text, to_language=target_lang, translator=engine)
            if result and result != text and len(result) > 2:
                return result.strip()
        except Exception:
            pass
        time.sleep(0.2)
    return text
