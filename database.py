import os
from datetime import datetime, date
from typing import Optional, List
from dotenv import load_dotenv
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select, func

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/smartpricing")
engine = create_engine(DATABASE_URL, echo=False)

def create_db_tables():
    SQLModel.metadata.create_all(engine)

class Product(SQLModel, table=True):
    __tablename__ = "product"
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(index=True, unique=True, max_length=64)
    name: str = Field(max_length=256)
    category: str = Field(max_length=128, index=True)
    fpn: Optional[str] = Field(default=None, max_length=256)
    ean: Optional[str] = Field(default=None, max_length=64)
    brand: Optional[str] = Field(default=None, max_length=128, index=True)
    my_price: float
    costo_acquisto: Optional[float] = Field(default=None)
    repricing_strategy: Optional[str] = Field(default=None, max_length=32)
    repricing_delta: Optional[float] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DailySnapshot(SQLModel, table=True):
    __tablename__ = "daily_snapshot"
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    snapshot_date: date = Field(index=True)
    my_price: float
    my_shipping_cost: float = Field(default=0.0)
    my_total_cost: float
    my_rank: int
    my_rank_with_shipping: int
    min_price: float
    min_price_with_shipping: float
    nb_offers: int
    nb_merchants: int
    popularity: int
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

class CompetitorOffer(SQLModel, table=True):
    __tablename__ = "competitor_offer"
    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_id: int = Field(foreign_key="daily_snapshot.id", index=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    snapshot_date: date = Field(index=True)
    merchant_name: str = Field(max_length=128, index=True)
    price: float
    rating: Optional[float] = Field(default=None)
    position: int

class Alert(SQLModel, table=True):
    __tablename__ = "alert"
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    merchant_name: Optional[str] = Field(default=None, max_length=128)
    threshold_price: float
    threshold_type: str = Field(max_length=32)
    notify_email: bool = Field(default=True)
    notify_ui: bool = Field(default=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AlertEvent(SQLModel, table=True):
    __tablename__ = "alert_event"
    id: Optional[int] = Field(default=None, primary_key=True)
    alert_id: int = Field(foreign_key="alert.id", index=True)
    merchant_name: str = Field(max_length=128)
    old_price: Optional[float] = Field(default=None)
    new_price: float
    is_read: bool = Field(default=False)
    triggered_at: datetime = Field(default_factory=datetime.utcnow)

class PriceSuggestion(SQLModel, table=True):
    __tablename__ = "price_suggestion"
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    suggestion_date: date = Field(index=True)
    suggested_price: float
    current_price: float
    min_competitor_price: float
    avg_competitor_price: float
    strategy_used: str = Field(max_length=32)
    margin_at_suggestion: Optional[float] = Field(default=None)
    reason: Optional[str] = Field(default=None, max_length=256)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RepricingStrategy(SQLModel, table=True):
    __tablename__ = "repricing_strategy"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=128)
    strategy_type: str = Field(max_length=32)
    delta_pct: float = Field(default=0.0)
    min_margin_pct: float = Field(default=15.0)
    is_active: bool = Field(default=True)
    priority: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SyncLog(SQLModel, table=True):
    __tablename__ = "sync_log"
    id: Optional[int] = Field(default=None, primary_key=True)
    sync_date: date = Field(index=True)
    status: str = Field(max_length=32)
    products_upserted: int = Field(default=0)
    snapshots_created: int = Field(default=0)
    competitor_offers_created: int = Field(default=0)
    alerts_triggered: int = Field(default=0)
    error_message: Optional[str] = Field(default=None)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = Field(default=None)

def get_latest_snapshot_per_product(session: Session) -> List[DailySnapshot]:
    subq = (select(DailySnapshot.product_id, func.max(DailySnapshot.snapshot_date).label("max_date")).group_by(DailySnapshot.product_id).subquery())
    return list(session.exec(select(DailySnapshot).join(subq, (DailySnapshot.product_id == subq.c.product_id) & (DailySnapshot.snapshot_date == subq.c.max_date))).all())

def get_unread_alert_count(session: Session) -> int:
    return session.exec(select(func.count(AlertEvent.id)).where(AlertEvent.is_read == False)).one() or 0

def get_all_merchants(session: Session) -> List[str]:
    return sorted(session.exec(select(CompetitorOffer.merchant_name).distinct()).all())

def get_kpi_summary(session: Session) -> dict:
    latest = get_latest_snapshot_per_product(session)
    if not latest:
        return {"price_index": 0.0, "win_rate": 0.0, "critical_sku_count": 0, "total_sku_count": 0}
    price_indexes, wins, critical = [], 0, 0
    for snap in latest:
        if snap.min_price and snap.min_price > 0:
            pi = round((snap.my_price / snap.min_price) * 100, 1)
            price_indexes.append(pi)
            if snap.my_rank == 1:
                wins += 1
            if pi > 110:
                critical += 1
    return {
        "price_index": round(sum(price_indexes)/len(price_indexes), 1) if price_indexes else 0.0,
        "win_rate": round((wins/len(latest))*100, 1),
        "critical_sku_count": critical,
        "total_sku_count": len(latest)
    }

if __name__ == "__main__":
    create_db_tables()
    print("Tabelle create con successo.")