"""
services/alphaposition_fetcher.py — SmartPricing Pro

Flusso:
  1. GET /TemporaryToken  → ottieni token (valido 1h)
  2. GET /OffersRanking   → scarica tutti i prodotti del catalogo con rank + BestOffers
  3. Upsert Product, crea DailySnapshot + CompetitorOffer per ogni riga

Viene chiamato dallo scheduler ogni giorno alle 02:00.
"""

from __future__ import annotations

import logging
import os
from datetime import date, datetime
from typing import Optional

import requests
from dotenv import load_dotenv
from sqlmodel import Session, select

from database import (
    CompetitorOffer,
    DailySnapshot,
    Product,
    SyncLog,
    create_db_tables,
    engine,
)

load_dotenv()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config da .env
# ---------------------------------------------------------------------------

ALPHAPOSITION_MERCHANT_ID = os.getenv("ALPHAPOSITION_MERCHANT_ID", "")
ALPHAPOSITION_API_KEY = os.getenv("ALPHAPOSITION_API_KEY", "")
BASE_URL = "https://services.7pixel.it/api/v1"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def _get_token() -> str:
    """
    Richiede un token temporaneo ad AlphaPosition.
    Il token è valido 1 ora. Ogni chiamata invalida il precedente.
    """
    url = (
        f"{BASE_URL}/TemporaryToken"
        f"?merchantid={ALPHAPOSITION_MERCHANT_ID}"
        f"&merchantkey={ALPHAPOSITION_API_KEY}"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("Token")
    if not token:
        raise ValueError(f"Token non trovato nella risposta: {data}")
    logger.info("Token AlphaPosition ottenuto, scade: %s", data.get("Expiration"))
    return token


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def _fetch_offers_ranking(token: str) -> list[dict]:
    """
    Scarica il ranking completo del catalogo in formato JSON.
    Ritorna la lista grezza di oggetti dalla response.
    """
    url = (
        f"{BASE_URL}/OffersRanking"
        f"?merchantid={ALPHAPOSITION_MERCHANT_ID}"
        f"&token={token}"
        f"&format=json"
    )
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    logger.info("OffersRanking: ricevuti %d prodotti", len(data))
    return data


# ---------------------------------------------------------------------------
# Parse e upsert
# ---------------------------------------------------------------------------

def _parse_price(value) -> Optional[float]:
    """Normalizza prezzi che potrebbero arrivare come int, float o None."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _upsert_product(session: Session, row: dict) -> Product:
    """
    Crea il Product se non esiste, altrimenti aggiorna my_price e campi TP.
    Il brand non viene toccato se già impostato manualmente.
    """
    sku = str(row["Sku"])
    product = session.exec(select(Product).where(Product.sku == sku)).first()

    if product is None:
        product = Product(
            sku=sku,
            name=row.get("Product") or sku,
            category=row.get("Category") or "Senza categoria",
            fpn=row.get("Fpn"),
            ean=str(row.get("Ean")) if row.get("Ean") else None,
            my_price=_parse_price(row.get("Price")) or 0.0,
        )
        session.add(product)
        session.flush()  # ottieni l'id senza commit
        logger.debug("Nuovo prodotto: SKU=%s — %s", sku, product.name)
    else:
        # Aggiorna sempre il prezzo corrente e i metadati TP
        product.my_price = _parse_price(row.get("Price")) or product.my_price
        product.category = row.get("Category") or product.category
        product.fpn = row.get("Fpn") or product.fpn
        if row.get("Ean"):
            product.ean = str(row["Ean"])
        product.updated_at = datetime.utcnow()

    return product


def _create_daily_snapshot(
    session: Session, product: Product, row: dict, today: date
) -> Optional[DailySnapshot]:
    """
    Crea il DailySnapshot per oggi se non esiste già.
    Se esiste (sync doppia nella stessa giornata) lo skippa.
    """
    existing = session.exec(
        select(DailySnapshot).where(
            DailySnapshot.product_id == product.id,
            DailySnapshot.snapshot_date == today,
        )
    ).first()

    if existing:
        logger.debug("Snapshot già presente per SKU=%s data=%s, skip", product.sku, today)
        return None

    snap = DailySnapshot(
        product_id=product.id,
        snapshot_date=today,
        my_price=_parse_price(row.get("Price")) or 0.0,
        my_shipping_cost=_parse_price(row.get("ShippingCost")) or 0.0,
        my_total_cost=_parse_price(row.get("TotalCost")) or 0.0,
        my_rank=int(row.get("Rank") or 0),
        my_rank_with_shipping=int(row.get("RankWithShippingCost") or 0),
        min_price=_parse_price(row.get("MinPrice")) or 0.0,
        min_price_with_shipping=_parse_price(row.get("MinPriceWithShippingCost")) or 0.0,
        nb_offers=int(row.get("NbOffers") or 0),
        nb_merchants=int(row.get("NbMerchants") or 0),
        popularity=int(row.get("Popularity") or 0),
    )
    session.add(snap)
    session.flush()
    return snap


def _create_competitor_offers(
    session: Session, snapshot: DailySnapshot, best_offers: list[dict], today: date,
    my_price: float = 0.0
) -> int:
    """
    Crea i CompetitorOffer dai BestOffers.
    Esclude outlier con prezzo < 50% del nostro (prodotto sbagliato sul listing).
    """
    OUTLIER_THRESHOLD = 0.5
    count = 0
    valid_position = 1
    for offer in best_offers or []:
        merchant = offer.get("Merchant") or offer.get("merchant") or "Sconosciuto"
        price = _parse_price(offer.get("Price") or offer.get("price"))
        if price is None:
            continue
        if my_price > 0 and price < my_price * OUTLIER_THRESHOLD:
            logger.debug("Outlier escluso: %s €%.2f (nostro €%.2f)", merchant, price, my_price)
            continue
        comp = CompetitorOffer(
            snapshot_id=snapshot.id,
            product_id=snapshot.product_id,
            snapshot_date=today,
            merchant_name=merchant,
            price=price,
            rating=_parse_price(offer.get("Rating") or offer.get("rating")),
            position=valid_position,
        )
        session.add(comp)
        count += 1
        valid_position += 1
    return count


# ---------------------------------------------------------------------------
# Entry point principale
# ---------------------------------------------------------------------------

def run_daily_sync() -> dict:
    """
    Esegue la sync completa:
      1. Ottieni token
      2. Scarica OffersRanking
      3. Per ogni prodotto: upsert Product + crea DailySnapshot + CompetitorOffer
      4. Aggiorna SyncLog

    Ritorna un dict con le statistiche della sync.
    """
    if not ALPHAPOSITION_MERCHANT_ID or not ALPHAPOSITION_API_KEY:
        raise EnvironmentError(
            "ALPHAPOSITION_MERCHANT_ID e ALPHAPOSITION_API_KEY devono essere in .env"
        )

    today = date.today()
    started_at = datetime.utcnow()

    # Apri log sync
    with Session(engine) as session:
        sync_log = SyncLog(
            sync_date=today,
            status="running",
            started_at=started_at,
        )
        session.add(sync_log)
        session.commit()
        session.refresh(sync_log)
        sync_log_id = sync_log.id

    products_upserted = 0
    snapshots_created = 0
    competitor_offers_created = 0
    error_message = None

    try:
        token = _get_token()
        rows = _fetch_offers_ranking(token)

        with Session(engine) as session:
            for row in rows:
                try:
                    product = _upsert_product(session, row)
                    products_upserted += 1

                    snapshot = _create_daily_snapshot(session, product, row, today)
                    if snapshot:
                        snapshots_created += 1
                        best_offers = row.get("BestOffers") or []
                        n = _create_competitor_offers(session, snapshot, best_offers, today, my_price=product.my_price)
                        competitor_offers_created += n

                except Exception as e:
                    logger.warning("Errore su SKU=%s: %s", row.get("Sku"), e)
                    # continua con il prossimo prodotto
                    continue

            session.commit()
            logger.info(
                "Sync completata: %d prodotti, %d snapshot, %d competitor offers",
                products_upserted, snapshots_created, competitor_offers_created,
            )

        status = "success"

    except Exception as e:
        error_message = str(e)
        status = "error"
        logger.error("Sync fallita: %s", e, exc_info=True)

    # Chiudi log sync
    with Session(engine) as session:
        sync_log = session.get(SyncLog, sync_log_id)
        if sync_log:
            sync_log.status = status
            sync_log.products_upserted = products_upserted
            sync_log.snapshots_created = snapshots_created
            sync_log.competitor_offers_created = competitor_offers_created
            sync_log.error_message = error_message
            sync_log.finished_at = datetime.utcnow()
            session.add(sync_log)
            session.commit()

    return {
        "status": status,
        "date": str(today),
        "products_upserted": products_upserted,
        "snapshots_created": snapshots_created,
        "competitor_offers_created": competitor_offers_created,
        "error_message": error_message,
    }


# ---------------------------------------------------------------------------
# Esecuzione diretta per test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_db_tables()
    result = run_daily_sync()
    print(result)