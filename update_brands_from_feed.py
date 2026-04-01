"""
update_brands_from_feed.py
1. Scarica feed XML → aggiorna brand, categoria per SKU matchati
2. Per prodotti ancora senza brand → inferisce dal nome prodotto
"""

import os
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
from dotenv import load_dotenv
from sqlmodel import Session, select

load_dotenv()

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import Product, engine

FEED_URL = "https://feeds.datafeedwatch.com/62653/5de2db28bf341d54bffbab7e2af0711a40c1d189.xml"
NS = "http://base.google.com/ns/1.0"


def parse_feed(url: str) -> dict:
    print(f"Scarico feed da {url}...")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    channel = root.find("channel")
    items = channel.findall("item")
    print(f"Trovati {len(items)} prodotti nel feed")

    feed_data = {}
    for item in items:
        sku = item.findtext(f"{{{NS}}}id")
        brand = item.findtext(f"{{{NS}}}brand") or ""
        product_type = item.findtext(f"{{{NS}}}product_type") or ""
        category = product_type.split(">")[0].strip() if product_type else ""
        if sku:
            feed_data[sku.strip()] = {
                "brand": brand.strip(),
                "category": category,
            }
    return feed_data


def update_db(feed_data: dict):
    updated = 0
    not_found = 0

    with Session(engine) as session:
        for sku, data in feed_data.items():
            product = session.exec(select(Product).where(Product.sku == sku)).first()
            if product:
                if data["brand"]:
                    product.brand = data["brand"]
                if data["category"]:
                    product.category = data["category"]
                product.updated_at = datetime.utcnow()
                updated += 1
            else:
                not_found += 1
        session.commit()

    print(f"✅ Aggiornati da feed: {updated} prodotti")
    print(f"⚠️  Non trovati nel DB: {not_found} SKU dal feed")


def infer_brands_from_name():
    """
    Per i prodotti ancora senza brand, cerca un match
    tra il nome prodotto e i brand già presenti nel DB.
    Es: "Hugo Boss Boss Bottled 75ml" → brand "Hugo Boss"
    """
    with Session(engine) as session:
        # Prendi tutti i brand distinti già nel DB
        known_brands = session.exec(
            select(Product.brand).where(Product.brand != None).distinct()
        ).all()
        known_brands = sorted([b for b in known_brands if b], key=len, reverse=True)
        # Ordine decrescente per lunghezza → match prima i brand più lunghi
        # (es. "Hugo Boss" prima di "Boss")

        # Prendi tutti i prodotti senza brand
        no_brand = session.exec(
            select(Product).where(Product.brand == None)
        ).all()

        fixed = 0
        for product in no_brand:
            name_lower = product.name.lower()
            for brand in known_brands:
                if brand.lower() in name_lower:
                    product.brand = brand
                    product.updated_at = datetime.utcnow()
                    fixed += 1
                    break

        session.commit()

    print(f"✅ Brand inferiti dal nome: {fixed} prodotti")


if __name__ == "__main__":
    feed_data = parse_feed(FEED_URL)
    update_db(feed_data)
    infer_brands_from_name()