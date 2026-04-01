"""
product_matcher.py
==================
Confronta il titolo di un prodotto del feed con il titolo
restituito da SerpAPI / Trovaprezzi.

Due livelli:
  1. Parsing semantico  — scompone entrambi i titoli in atomi
                          (brand, linea, concentrazione, formato, genere)
  2. Fuzzy matching     — misura la somiglianza con rapidfuzz

Logica di decisione:
  - ml diversi               → RIFIUTA sempre (hard filter)
  - brand assente            → RIFIUTA sempre (hard filter)
  - score >= 90              → MATCH automatico
  - score 70-89              → MATCH incerto (accettato, loggato)
  - score < 70               → RIFIUTA

Dipendenza: pip install rapidfuzz
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional
from rapidfuzz import fuzz

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SOGLIE
# ---------------------------------------------------------------------------

SCORE_AUTO_MATCH = 90
SCORE_UNCERTAIN  = 70

# ---------------------------------------------------------------------------
# DIZIONARI DI NORMALIZZAZIONE
# ---------------------------------------------------------------------------

CONCENTRATION_MAP = {
    "eau de parfum":      "edp",
    "e.d.p":              "edp",
    "e.d.p.":             "edp",
    "edp":                "edp",
    "parfum":             "edp",
    "eau de toilette":    "edt",
    "e.d.t":              "edt",
    "e.d.t.":             "edt",
    "edt":                "edt",
    "toilette":           "edt",
    "eau de cologne":     "edc",
    "e.d.c":              "edc",
    "edc":                "edc",
    "cologne":            "edc",
    "parfum extrait":     "extrait",
    "extrait de parfum":  "extrait",
    "extrait":            "extrait",
    "parfum de toilette": "pdt",
    "pdt":                "pdt",
    "body lotion":        "lotion",
    "lotion corpo":       "lotion",
    "lotion":             "lotion",
    "shower gel":         "shower",
    "gel doccia":         "shower",
    "crema corpo":        "cream",
    "body cream":         "cream",
    "crema":              "cream",
    "cream":              "cream",
}

GENDER_MAP = {
    "donna":  "f",
    "woman":  "f",
    "women":  "f",
    "femme":  "f",
    "her":    "f",
    "uomo":   "m",
    "man":    "m",
    "men":    "m",
    "homme":  "m",
    "him":    "m",
    "unisex": "u",
    "misto":  "u",
}

STOP_WORDS = {
    "spray", "vapo", "vaporisateur", "atomiseur", "ml", "fl", "oz",
    "new", "nuovo", "edition", "edizione", "limited", "limitata",
    "set", "kit", "cofanetto", "gift", "regalo", "ricarica", "refill",
    "tester", "travel", "miniatura", "mini", "size", "formato",
    "profumo", "fragrance", "fragranza", "parfumerie",
    "the", "di", "de", "du", "la", "le", "les", "il", "lo",
}


# ---------------------------------------------------------------------------
# DATACLASS TOKEN
# ---------------------------------------------------------------------------

@dataclass
class ProductTokens:
    brand:         str           = ""
    line:          str           = ""
    concentration: str           = ""
    gender:        str           = ""
    size_ml:       Optional[int] = None
    extra_tokens:  list          = field(default_factory=list)

    def key_string(self) -> str:
        """Stringa comparabile per fuzzy matching (size_ml escluso, è un hard filter)."""
        parts = [self.brand, self.line, self.concentration, self.gender] + self.extra_tokens
        return " ".join(p for p in parts if p).strip()


# ---------------------------------------------------------------------------
# HELPERS DI PARSING
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[°•·/\\|°º]", " ", text)
    text = re.sub(r"n[°º.]?\s*(\d)", r"n\1", text)   # "N°5" → "n5"
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_size_ml(text: str) -> Optional[int]:
    matches = re.findall(r"(\d+(?:[.,]\d+)?)\s*ml", text, re.IGNORECASE)
    values  = []
    for m in matches:
        try:
            v = int(float(m.replace(",", ".")))
            if 1 <= v <= 5000:
                values.append(v)
        except ValueError:
            pass
    return max(values) if values else None


def _extract_concentration(text: str) -> tuple[str, str]:
    for phrase in sorted(CONCENTRATION_MAP.keys(), key=len, reverse=True):
        if phrase in text:
            return CONCENTRATION_MAP[phrase], text.replace(phrase, " ", 1)
    return "", text


def _extract_gender(text: str) -> tuple[str, str]:
    for word, token in GENDER_MAP.items():
        pattern = r"\b" + re.escape(word) + r"\b"
        if re.search(pattern, text):
            text = re.sub(pattern, " ", text)
            return token, text
    return "", text


# ---------------------------------------------------------------------------
# PARSING SEMANTICO
# ---------------------------------------------------------------------------

def parse_title(title: str, brand_hint: str = "") -> ProductTokens:
    """
    Scompone un titolo prodotto negli atomi semantici.
    brand_hint: brand noto dal feed (es. "Dior"), cercato e rimosso per primo.
    """
    text = _normalize(title)

    # 1. ml → rimosso (hard filter separato)
    size_ml = _extract_size_ml(text)
    text    = re.sub(r"\d+(?:[.,]\d+)?\s*ml", " ", text, flags=re.IGNORECASE)

    # 2. Concentrazione
    concentration, text = _extract_concentration(text)

    # 3. Genere
    gender, text = _extract_gender(text)

    # 4. Brand (se noto dal feed)
    brand = ""
    if brand_hint:
        brand_norm = _normalize(brand_hint)
        if brand_norm in text:
            brand = brand_norm
            text  = text.replace(brand_norm, " ", 1)

    # 5. Token rimasti
    tokens = [t for t in text.split() if t not in STOP_WORDS and len(t) > 1]
    line   = tokens[0] if tokens else ""
    extras = tokens[1:] if len(tokens) > 1 else []

    return ProductTokens(
        brand         = brand,
        line          = line,
        concentration = concentration,
        gender        = gender,
        size_ml       = size_ml,
        extra_tokens  = extras,
    )


# ---------------------------------------------------------------------------
# MATCH PRINCIPALE
# ---------------------------------------------------------------------------

def match_product(
    feed_title:   str,
    api_title:    str,
    feed_brand:   str = "",
    feed_size_ml: str = "",
) -> tuple[bool, int]:
    """
    Confronta il titolo del feed con quello restituito dall'API.

    Ritorna:
        (match: bool, score: int 0-100)
    """
    # Hard filter 1 — brand obbligatorio
    if feed_brand:
        if _normalize(feed_brand) not in _normalize(api_title):
            log.debug("RIFIUTO brand: '%s' non in '%s'", feed_brand, api_title[:60])
            return False, 0

    # Hard filter 2 — ml devono combaciare esattamente
    if feed_size_ml:
        cleaned = re.sub(r"[^\d]", "", str(feed_size_ml))
        if cleaned:
            expected_ml = int(cleaned)
            found_ml    = _extract_size_ml(api_title)
            if found_ml is not None and expected_ml != found_ml:
                log.debug(
                    "RIFIUTO size: feed=%dml api=%dml '%s'",
                    expected_ml, found_ml, api_title[:60]
                )
                return False, 0

    # Parsing semantico di entrambi i titoli
    feed_tokens = parse_title(feed_title, brand_hint=feed_brand)
    api_tokens  = parse_title(api_title,  brand_hint=feed_brand)

    feed_str = feed_tokens.key_string()
    api_str  = api_tokens.key_string()

    if not feed_str or not api_str:
        return False, 0

    # token_set_ratio: ignora l'ordine delle parole
    # "Chanel N5 EDP" vs "N°5 Chanel Eau de Parfum" → score alto
    score = fuzz.token_set_ratio(feed_str, api_str)

    if score >= SCORE_AUTO_MATCH:
        log.debug("MATCH [%d] '%s' ↔ '%s'", score, feed_str[:40], api_str[:40])
        return True, score

    if score >= SCORE_UNCERTAIN:
        log.info("MATCH INCERTO [%d] '%s' ↔ '%s'", score, feed_str[:40], api_str[:40])
        return True, score

    log.debug("RIFIUTO [%d] '%s' ↔ '%s'", score, feed_str[:40], api_str[:40])
    return False, 0


# ---------------------------------------------------------------------------
# TEST DA RIGA DI COMANDO
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    test_cases = [
        ("Dior Sauvage Eau de Toilette 60ml",  "Dior Sauvage Eau de Toilette 60 ml - Notino",        "Dior",    "60",  True),
        ("Chanel N°5 Eau de Parfum 100ml",     "Chanel 5 profumo donna 100ml",                        "Chanel",  "100", True),
        ("Chanel N°5 Eau de Parfum 100ml",     "N.5 Chanel EDP Vapo Femme 100ml",                     "Chanel",  "100", True),
        ("Dior Sauvage EDP 100ml",             "Dior Sauvage EDT 60ml",                                "Dior",    "100", False),
        ("Armani Acqua di Giò EDT 50ml",       "Armani Acqua di Gio Homme Eau de Toilette 50ml",      "Armani",  "50",  True),
        ("Bleu de Chanel EDP 100ml",           "Dior Sauvage EDP 100ml",                              "Chanel",  "100", False),
        ("Dior Sauvage EDP 100ml",             "Sauvage Dior Eau de Parfum 100ml Uomo",               "Dior",    "100", True),
    ]

    print(f"\n{'FEED':<42} {'API':<45} {'SC':>4}  {'ATT':>5}  RIS")
    print("-" * 110)
    for feed, api, brand, size, expected in test_cases:
        matched, score = match_product(feed, api, brand, size)
        ok = "✅" if matched == expected else "❌ ERRORE"
        print(f"{feed[:40]:<42} {api[:43]:<45} {score:>4}  {str(expected):>5}  {ok}")