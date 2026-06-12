from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

LOCALES_DIR = Path(__file__).resolve().parent / "locales"

_translations: Dict[str, Dict[str, Any]] = {}


def load_translations() -> None:
    global _translations
    if not LOCALES_DIR.exists():
        return
    for json_file in LOCALES_DIR.glob("*.json"):
        lang = json_file.stem
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                _translations[lang] = json.load(f)
        except Exception:
            # Silently ignore or skip parsing errors on malformed JSON
            pass


def translate(lang: str, key: str, default: str = "") -> str:
    """Look up key in the translations dictionary for `lang` with fallback to `en`."""
    global _translations
    if not _translations:
        load_translations()

    lang_translations = _translations.get(lang, {})
    if key in lang_translations:
        return str(lang_translations[key])

    # Fallback to English
    en_translations = _translations.get("en", {})
    if key in en_translations:
        return str(en_translations[key])

    return default if default else key
