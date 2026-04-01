"""
price_fetcher.py
================
Scarica i prezzi competitor da SerpAPI (Google Shopping) e Trovaprezzi,
li valida tramite product_matcher, li deduplica, e restituisce un dict
compatibile con lo schema PriceRecord già esistente nell'app:

    { "comp_1_name": "Notino", "comp_1_price": 109.0, ... }

Uso da state.py:
    from price_fetcher import build_competitor_prices, parse_xml_feed

Dipendenze: httpx (già in Reflex), rapidfuzz (pip install rapidfuzz)
"""

import re
import logging
import xml.etree.ElementTree as ET
from typing import Optional
import httpx

from .product_matcher import match_product

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------------

SERPAPI_KEY = "LA_TUA_CHIAVE_SERPAPI"   # <-- unico valore da aggiungere

# Competitor autorizzati: chiave interna → pattern da cercare nel campo
# "source" o "title" del risultato Google Shopping.
COMPETITOR_MAP: dict[str, list[str]] = {
    "Notino":    ["notino"],
    "Pinalli":   ["pinalli"],
    "Douglas":   ["douglas"],
    "Sephora":   ["sephora"],
    "Sensation": ["sensation", "sensationprofumerie"],
}


# ---------------------------------------------------------------------------
# 1. PARSING FEED XML
# ---------------------------------------------------------------------------

def parse_xml_feed(xml_url: str) -> list[dict]:
    """
    Scarica e parsa il feed XML DataFeedWatch.
    Ritorna lista di dict con: sku, product_name, brand, size_ml,
                               my_price, image_url, category, ean (se presente)
    """
    try:
        resp = httpx.get(xml_url, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
    except Exception as e:
        log.error("Errore download feed XML: %s", e)
        return []

    products = []
    for item in root.findall(".//item"):

        def t(tag: str) -> str:
            el = item.find(tag)
            return el.text.strip() if el is not None and el.text else ""

        title     = t("title") or t("g:title")
        price_raw = t("g:price") or t("price")
        size_raw  = t("g:size") or t("size") or ""

        # Estrai ml dal campo size dedicato, altrimenti dal titolo
        size_ml = _extract_ml_str(size_raw) or _extract_ml_str(title)

        products.append({
            "sku":          t("g:id") or t("id"),
            "product_name": title,
            "brand":        t("g:brand") or t("brand"),
            "category":     t("g:product_type") or t("product_type") or "Tutte",
            "image_url":    t("g:image_link") or t("image_link"),
            "ean":          t("g:gtin") or t("gtin") or "",
            "size_ml":      size_ml,
            "my_price":     _to_float(price_raw.split()[0] if price_raw else "") or 0.0,
        })

    log.info("Feed XML: %d prodotti caricati", len(products))
    return products


# ---------------------------------------------------------------------------
# 2. CHIAMATA SERPAPI GOOGLE SHOPPING
# ---------------------------------------------------------------------------

def _fetch_serpapi(query: str) -> list[dict]:
    params = {
        "engine":  "google_shopping",
        "q":       query,
        "gl":      "it",
        "hl":      "it",
        "api_key": SERPAPI_KEY,
        "num":     20,
    }
    try:
        resp = httpx.get("https://serpapi.com/search", params=params, timeout=20)
        resp.raise_for_status()
        results = resp.json().get("shopping_results", [])
        log.info("SerpAPI '%s' → %d risultati", query[:50], len(results))
        return results
    except Exception as e:
        log.warning("SerpAPI fallita per '%s': %s", query[:50], e)
        return []


# ---------------------------------------------------------------------------
# 3. CHIAMATA TROVAPREZZI
# ---------------------------------------------------------------------------

def _fetch_trovaprezzi(
    api_key:     str,
    merchant_id: str,
    ean:         Optional[str] = None,
    query:       Optional[str] = None,
) -> list[dict]:
    if not api_key or (not ean and not query):
        return []
    params = {"apikey": api_key, "merchant": merchant_id}
    if ean:
        params["ean"] = ean
    else:
        params["q"] = query
    try:
        resp = httpx.get("https://api.trovaprezzi.it/offers", params=params, timeout=20)
        resp.raise_for_status()
        return resp.json().get("offers", [])
    except Exception as e:
        log.warning("Trovaprezzi fallita: %s", e)
        return []


# ---------------------------------------------------------------------------
# 4. IDENTIFICAZIONE COMPETITOR
# ---------------------------------------------------------------------------

def _match_competitor(source: str, title: str) -> Optional[str]:
    """
    Ritorna la chiave interna del competitor (es. 'Notino') se autorizzato.
    Cerca sia nel campo source che nel title.
    """
    text = (source + " " + title).lower()
    for comp_key, patterns in COMPETITOR_MAP.items():
        if any(p in text for p in patterns):
            return comp_key
    return None


# ---------------------------------------------------------------------------
# 5. HELPERS
# ---------------------------------------------------------------------------

def _build_query(product: dict) -> str:
    """Brand + Nome + Formato ml. Senza il formato Google restituisce il flacone più piccolo."""
    brand   = product.get("brand", "").strip()
    name    = product.get("product_name", "").strip()
    size_ml = re.sub(r"[^\d]", "", str(product.get("size_ml", "")))
    suffix  = f"{size_ml}ml" if size_ml else ""
    return f"{brand} {name} {suffix}".strip()


def _extract_ml_str(text: str) -> str:
    """Estrae il valore ml come stringa (es. '100') da un testo."""
    matches = re.findall(r"(\d+)\s*ml", text, re.IGNORECASE)
    values  = [int(m) for m in matches if 1 <= int(m) <= 5000]
    return str(max(values)) if values else ""


def _to_float(val) -> Optional[float]:
    if val is None:
        return None
    cleaned = re.sub(r"[^\d.,]", "", str(val)).replace(",", ".")
    parts   = cleaned.split(".")
    if len(parts) > 2:
        cleaned = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return round(float(cleaned), 2)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# 6. DEDUPLICATION
# ---------------------------------------------------------------------------

def _dedup_and_merge(
    serpapi_found:     dict[str, dict],
    trovaprezzi_found: dict[str, dict],
) -> dict[str, dict]:
    """
    Per ogni competitor che compare in entrambe le fonti,
    prende semplicemente il prezzo più basso.

    Input:  { "Notino": {"price": X, "url": Y}, ... }
    Output: { "Notino": {"price": X, "url": Y, "fonte": Z}, ... }
    """
    merged = {}

    for comp in set(serpapi_found) | set(trovaprezzi_found):
        sp = serpapi_found.get(comp)
        tp = trovaprezzi_found.get(comp)

        # Solo una fonte ha il dato
        if sp is None:
            merged[comp] = {**tp, "fonte": "trovaprezzi"}
            continue
        if tp is None:
            merged[comp] = {**sp, "fonte": "serpapi"}
            continue

        # Entrambe hanno il dato → vince il prezzo più basso
        sp_price = sp.get("price") or 0
        tp_price = tp.get("price") or 0

        if tp_price > 0 and (sp_price == 0 or tp_price < sp_price):
            merged[comp] = {**tp, "fonte": "trovaprezzi"}
            log.info("  [dedup] %s → TP €%.2f batte SP €%.2f", comp, tp_price, sp_price)
        else:
            merged[comp] = {**sp, "fonte": "serpapi"}

    return merged


# ---------------------------------------------------------------------------
# 7. ENTRY POINT PRINCIPALE
# ---------------------------------------------------------------------------

def build_competitor_prices(
    product:                 dict,
    trovaprezzi_api_key:     str,
    trovaprezzi_merchant_id: str,
    use_serpapi:             bool = False,
    use_trovaprezzi:         bool = True,
) -> dict:
    """
    Pipeline completo per un singolo prodotto.

    Ritorna un dict direttamente iniettabile in PriceRecord:
        {
          "comp_1_name": "Notino",  "comp_1_price": 109.0,
          "comp_2_name": "Douglas", "comp_2_price": 115.0,
          ...
        }
    I competitor non trovati vengono impostati a "-" e 0.0.
    """
    query        = _build_query(product)
    feed_title   = product.get("product_name", "")
    feed_brand   = product.get("brand", "")
    feed_size_ml = str(product.get("size_ml", ""))

    # ------------------------------------------------------------------ #
    # SerpAPI
    # ------------------------------------------------------------------ #
    serpapi_found: dict[str, dict] = {}

    if use_serpapi:
        for raw in _fetch_serpapi(query):
            api_title  = raw.get("title", "")
            api_source = raw.get("source", "")

            # Competitor autorizzato?
            comp = _match_competitor(api_source, api_title)
            if comp is None:
                continue

            # Match semantico + fuzzy
            matched, score = match_product(
                feed_title   = feed_title,
                api_title    = api_title,
                feed_brand   = feed_brand,
                feed_size_ml = feed_size_ml,
            )
            if not matched:
                continue

            price = _to_float(raw.get("price"))
            if price is None:
                continue

            # Tieni il prezzo più basso se il competitor appare più volte
            existing = serpapi_found.get(comp, {}).get("price")
            if existing is None or price < existing:
                serpapi_found[comp] = {"price": price, "url": raw.get("link")}
                log.info("  [SerpAPI] %s → €%.2f (score %d) '%s'", comp, price, score, api_title[:50])

    # ------------------------------------------------------------------ #
    # Trovaprezzi
    # ------------------------------------------------------------------ #
    trovaprezzi_found: dict[str, dict] = {}

    if use_trovaprezzi:
        ean        = product.get("ean") or None
        raw_offers = _fetch_trovaprezzi(
            trovaprezzi_api_key,
            trovaprezzi_merchant_id,
            ean   = ean,
            query = None if ean else query,
        )
        for offer in raw_offers:
            # Adatta i nomi campo alla documentazione reale di Trovaprezzi
            api_source = offer.get("merchant_name", "")
            api_title  = offer.get("product_name", "")

            comp = _match_competitor(api_source, api_title)
            if comp is None:
                continue

            matched, score = match_product(
                feed_title   = feed_title,
                api_title    = api_title,
                feed_brand   = feed_brand,
                feed_size_ml = feed_size_ml,
            )
            if not matched:
                continue

            price = _to_float(offer.get("price"))
            if price is None:
                continue

            existing = trovaprezzi_found.get(comp, {}).get("price")
            if existing is None or price < existing:
                trovaprezzi_found[comp] = {"price": price, "url": offer.get("offer_url")}
                log.info("  [TP] %s → €%.2f (score %d) '%s'", comp, price, score, api_title[:50])

    # ------------------------------------------------------------------ #
    # Deduplication
    # ------------------------------------------------------------------ #
    merged = _dedup_and_merge(serpapi_found, trovaprezzi_found)

    # ------------------------------------------------------------------ #
    # Mappa nel formato PriceRecord (comp_1 … comp_5)
    # ------------------------------------------------------------------ #
    result: dict = {}
    for idx, (comp_name, data) in enumerate(merged.items(), start=1):
        if idx > 5:
            break
        result[f"comp_{idx}_name"]  = comp_name
        result[f"comp_{idx}_price"] = data.get("price") or 0.0
        result[f"comp_{idx}_fonte"] = data.get("fonte", "unknown")

    # Slot vuoti
    for idx in range(len(merged) + 1, 6):
        result[f"comp_{idx}_name"]  = "-"
        result[f"comp_{idx}_price"] = 0.0
        result[f"comp_{idx}_fonte"] = "unknown"

    return result