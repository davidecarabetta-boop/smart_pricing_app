import reflex as rx
from typing import List, Dict, Any, Optional
import datetime
import os
import asyncio
from sqlmodel import Session, select, func
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import (
    Product, DailySnapshot, CompetitorOffer,
    SyncLog, engine
)


class State(rx.State):

    # ---------------------------------------------------------------------------
    # UI STATE
    # ---------------------------------------------------------------------------
    is_loading: bool = False
    sort_column: str = "price_index"
    sort_reverse: bool = True
    page_number: int = 1
    items_per_page: int = 50
    search_product: str = ""
    filter_category: str = "Tutte"
    filter_brand: str = "Tutti"
    filter_competitor: List[str] = []
    selected_sku: str = ""

    # Competitor preferiti
    comp_box_1: str = "Notino"
    comp_box_2: str = "Sephora"
    comp_box_3: str = "Douglas"
    preferred_competitors: List[str] = ["Notino", "Sephora", "Douglas", "", ""]

    # Sync
    sync_status: str = "In attesa..."
    sync_progress: int = 0
    sync_current_product: str = ""
    last_sync_count: int = 0
    is_syncing: bool = False

    # GA4
    ga4_property_id: str = ""
    ga4_json_key: str = ""
    ga4_status: str = "Non configurato"
    last_sync_ga4: str = "Mai"
    is_syncing_ga4: bool = False

    # ---------------------------------------------------------------------------
    # DATI IN MEMORIA
    # ---------------------------------------------------------------------------
    _products_raw: List[Dict[str, Any]] = []
    _kpi: Dict[str, Any] = {}
    _chart_data_raw: List[Dict[str, Any]] = []
    _categories_raw: List[str] = []
    _brands_raw: List[str] = []
    _merchants_raw: List[str] = []
    _ga4_data: Dict[str, Any] = {}  # {sku: {revenue, units}}

    # Dati prodotto selezionato (details)
    _selected_product: Dict[str, Any] = {}
    _selected_competitors: List[Dict[str, Any]] = []
    _selected_positioning_history: List[Dict[str, Any]] = []
    _selected_price_history: List[Dict[str, Any]] = []

    # ---------------------------------------------------------------------------
    # ON LOAD
    # ---------------------------------------------------------------------------

    @rx.event
    def on_load(self):
        self.is_loading = True
        self._load_data()
        if self.selected_sku:
            self._load_product_detail()
        self.is_loading = False

    def _load_data(self):
        with Session(engine) as session:
            today = datetime.date.today()

            rows = session.exec(
                select(Product, DailySnapshot)
                .join(DailySnapshot, DailySnapshot.product_id == Product.id)
                .where(DailySnapshot.snapshot_date == today)
            ).all()

            products = []
            for product, snap in rows:
                # Calcola min_price dalle CompetitorOffer filtrate (esclude outlier < 50%)
                valid_offers = session.exec(
                    select(CompetitorOffer)
                    .where(
                        CompetitorOffer.product_id == product.id,
                        CompetitorOffer.snapshot_date == today,
                        CompetitorOffer.price >= product.my_price * 0.5,
                    )
                    .order_by(CompetitorOffer.price)
                ).all()
                real_min_price = valid_offers[0].price if valid_offers else snap.min_price
                if real_min_price and real_min_price > 0:
                    pi = round((snap.my_price / real_min_price) * 100, 1)
                else:
                    pi = 100.0

                best_offer = session.exec(
                    select(CompetitorOffer)
                    .where(
                        CompetitorOffer.product_id == product.id,
                        CompetitorOffer.snapshot_date == today,
                        CompetitorOffer.price >= product.my_price * 0.5,
                    )
                    .order_by(CompetitorOffer.price)
                ).first()

                second_offer = session.exec(
                    select(CompetitorOffer)
                    .where(
                        CompetitorOffer.product_id == product.id,
                        CompetitorOffer.snapshot_date == today,
                        CompetitorOffer.price >= product.my_price * 0.5,
                        CompetitorOffer.price != (best_offer.price if best_offer else 0),
                    )
                    .order_by(CompetitorOffer.price)
                ).first()

                min_comp_name = best_offer.merchant_name if best_offer else "-"
                min_comp_price = best_offer.price if best_offer else 0.0
                sec_comp_name = second_offer.merchant_name if second_offer else "-"
                sec_comp_price = second_offer.price if second_offer else 0.0

                products.append({
                    "id": product.id,
                    "sku": product.sku,
                    "name": product.name,
                    "brand": product.brand or "-",
                    "category": product.category,
                    "my_price": product.my_price,
                    "my_price_fmt": f"{product.my_price:.2f}",
                    "price": f"{product.my_price:.2f}",
                    "min_price": real_min_price,
                    "min_price_fmt": f"€{real_min_price:.2f}" if real_min_price else "-",
                    "min_comp_name": min_comp_name,
                    "min_comp_price": min_comp_price,
                    "min_comp_price_fmt": f"€{min_comp_price:.2f}" if min_comp_price else "-",
                    "comp_1_name": min_comp_name,
                    "comp_1_price": f"{min_comp_price:.2f}" if min_comp_price else "N/D",
                    "comp_2_name": sec_comp_name,
                    "comp_2_price": f"{sec_comp_price:.2f}" if sec_comp_price else "N/D",
                    "comp_price_filtered": "",
                    "price_index": pi,
                    "price_index_fmt": f"{pi:.1f}",
                    "my_rank": snap.my_rank,
                    "nb_merchants": snap.nb_merchants,
                    "popularity": snap.popularity,
                    "pos": f"#{snap.my_rank}",
                    "revenue": "0.00",
                    "units": "0",
                    "color": "red" if pi > 110 else ("orange" if pi > 103 else "green"),
                    "pi_color": "red" if pi > 110 else ("orange" if pi > 103 else "green"),
                })

            self._products_raw = products

            total = len(products)
            if total > 0:
                avg_pi = round(sum(p["price_index"] for p in products) / total, 1)
                wins = sum(1 for p in products if p["my_rank"] == 1)
                critical = sum(1 for p in products if p["price_index"] > 110)
                win_rate = round((wins / total) * 100, 1)
            else:
                avg_pi, wins, critical, win_rate = 0.0, 0, 0, 0.0

            self._kpi = {
                "price_index": avg_pi,
                "win_rate": win_rate,
                "win_count": wins,
                "critical_sku_count": critical,
                "total_sku_count": total,
            }

            # Grafico temporale
            cutoff = today - datetime.timedelta(days=29)
            daily_rows = session.exec(
                select(
                    DailySnapshot.snapshot_date,
                    func.avg(DailySnapshot.my_price / DailySnapshot.min_price * 100).label("avg_pi"),
                    func.avg(DailySnapshot.my_rank).label("avg_rank"),
                )
                .where(
                    DailySnapshot.snapshot_date >= cutoff,
                    DailySnapshot.min_price > 0,
                )
                .group_by(DailySnapshot.snapshot_date)
                .order_by(DailySnapshot.snapshot_date)
            ).all()

            self._chart_data_raw = [
                {
                    "name": row.snapshot_date.strftime("%d/%m"),
                    "price_index": round(float(row.avg_pi), 1),
                    "avg_rank": round(float(row.avg_rank), 1),
                }
                for row in daily_rows
            ]

            cats = session.exec(select(Product.category).distinct()).all()
            self._categories_raw = ["Tutte"] + sorted([c for c in cats if c])

            brands = session.exec(select(Product.brand).distinct()).all()
            self._brands_raw = ["Tutti"] + sorted([b for b in brands if b])

            merchants = session.exec(
                select(CompetitorOffer.merchant_name).distinct()
            ).all()
            self._merchants_raw = sorted([m for m in merchants if m])

    def _load_product_detail(self):
        """Carica i dati del prodotto selezionato per la pagina details."""
        if not self.selected_sku:
            return

        with Session(engine) as session:
            today = datetime.date.today()

            product = session.exec(
                select(Product).where(Product.sku == self.selected_sku)
            ).first()

            if not product:
                self._selected_product = {}
                return

            snap = session.exec(
                select(DailySnapshot)
                .where(
                    DailySnapshot.product_id == product.id,
                    DailySnapshot.snapshot_date == today,
                )
            ).first()

            if snap and snap.min_price and snap.min_price > 0:
                pi = round((snap.my_price / snap.min_price) * 100, 1)
                pi_color = "#DC2626" if pi > 110 else ("#F59E0B" if pi > 103 else "#16A34A")
                suggested = round(snap.min_price - 0.01, 2)
            else:
                pi = 100.0
                pi_color = "#64748B"
                suggested = product.my_price

            self._selected_product = {
                "name": product.name,
                "brand": product.brand or "-",
                "category": product.category,
                "sku": product.sku,
                "price": f"{product.my_price:.2f}",
                "pos": f"#{snap.my_rank}" if snap else "#-",
                "pos_color": "green" if snap and snap.my_rank == 1 else ("blue" if snap and snap.my_rank <= 3 else "red"),
                "revenue": "0.00",
                "units": "0",
                "price_index_label": f"{pi:.1f}",
                "price_index_color": pi_color,
                "suggested_price": f"{suggested:.2f}",
            }

            # Top competitor per questo prodotto
            offers = session.exec(
                select(CompetitorOffer)
                .where(
                    CompetitorOffer.product_id == product.id,
                    CompetitorOffer.snapshot_date == today,
                )
                .order_by(CompetitorOffer.position)
                .limit(5)
            ).all()

            dot_colors = ["#EF4444", "#F59E0B", "#8B5CF6", "#10B981", "#6366F1"]
            competitors = []
            for i, offer in enumerate(offers):
                delta_pct = ((offer.price - product.my_price) / product.my_price) * 100
                delta_str = f"+{delta_pct:.1f}%" if delta_pct >= 0 else f"{delta_pct:.1f}%"
                competitors.append({
                    "name": offer.merchant_name,
                    "price": f"{offer.price:.2f}",
                    "delta": delta_str,
                    "delta_color": "green" if delta_pct > 0 else "red",
                    "availability": "Disponibile",
                    "dot_color": dot_colors[i],
                })
            self._selected_competitors = competitors

            # Storico posizionamento (ultimi 30gg)
            cutoff = today - datetime.timedelta(days=29)
            history_snaps = session.exec(
                select(DailySnapshot)
                .where(
                    DailySnapshot.product_id == product.id,
                    DailySnapshot.snapshot_date >= cutoff,
                )
                .order_by(DailySnapshot.snapshot_date)
            ).all()

            self._selected_positioning_history = [
                {
                    "name": s.snapshot_date.strftime("%d/%m"),
                    "pos": s.my_rank,
                    "score": max(1, 6 - s.my_rank),  # invertito: rank 1 → score 5 (alto)
                }
                for s in history_snaps
            ]

            # Storico prezzi (mio vs min competitor)
            self._selected_price_history = [
                {
                    "name": s.snapshot_date.strftime("%d/%m"),
                    "price": s.my_price,
                    "market": s.min_price,
                }
                for s in history_snaps
            ]

    # ---------------------------------------------------------------------------
    # COMPUTED VARS — KPI HOME
    # ---------------------------------------------------------------------------

    @rx.var
    def kpi_price_index(self) -> float:
        return self._kpi.get("price_index", 0.0)

    @rx.var
    def kpi_price_index_fmt(self) -> str:
        return f"{self._kpi.get('price_index', 0.0):.1f}"

    @rx.var
    def kpi_win_rate(self) -> str:
        return f"{self._kpi.get('win_rate', 0.0):.1f}%"

    @rx.var
    def kpi_critical_sku(self) -> int:
        return self._kpi.get("critical_sku_count", 0)

    @rx.var
    def kpi_total_sku(self) -> int:
        return self._kpi.get("total_sku_count", 0)

    @rx.var
    def kpi_pi_color(self) -> str:
        pi = self._kpi.get("price_index", 100.0)
        if pi > 103:
            return "red"
        if pi > 100:
            return "orange"
        return "green"

    @rx.var
    def kpi_pi_status(self) -> str:
        pi = self._kpi.get("price_index", 100.0)
        if pi > 110:
            return "Fuori Mercato"
        if pi > 103:
            return "Attenzione"
        if pi > 100:
            return "Quasi Allineato"
        return "Competitivo"

    # Alias per compatibilità home.py
    @rx.var
    def price_index(self) -> int:
        return int(self._kpi.get("price_index", 100.0))

    @rx.var
    def price_index_float(self) -> float:
        return self._kpi.get("price_index", 0.0)

    @rx.var
    def win_rate(self) -> str:
        return f"{self._kpi.get('win_rate', 0.0):.0f}%"

    @rx.var
    def win_rate_count(self) -> int:
        return self._kpi.get("win_count", 0)

    @rx.var
    def critical_risk(self) -> int:
        return self._kpi.get("critical_sku_count", 0)

    @rx.var
    def total_products(self) -> int:
        return self._kpi.get("total_sku_count", 0)

    @rx.var
    def pi_color(self) -> str:
        return self.kpi_pi_color

    @rx.var
    def pi_status(self) -> str:
        return self.kpi_pi_status

    @rx.var
    def pi_pts(self) -> str:
        pi = self._kpi.get("price_index", 100.0)
        delta = round(pi - 100.0, 1)
        return f"+{delta} pts" if delta >= 0 else f"{delta} pts"

    @rx.var
    def risk_color(self) -> str:
        cr = self._kpi.get("critical_sku_count", 0)
        if cr > 10:
            return "red"
        if cr > 0:
            return "orange"
        return "green"

    @rx.var
    def margin_opp(self) -> str:
        products = list(self._products_raw)
        total = sum(
            (p["my_price"] - p["min_comp_price"])
            for p in products
            if p.get("my_rank", 0) == 1 and p.get("min_comp_price", 0) > p["my_price"]
        )
        return f"€{total:.2f}" if total > 0 else "€0.00"

    # Competitor aggressiveness — usa preferred_competitors
    @rx.var
    def comp_aggr_1(self) -> str:
        prefs = list(self.preferred_competitors)
        return self._calc_comp_aggr(prefs[0] if len(prefs) > 0 else "")

    @rx.var
    def comp_label_1(self) -> str:
        return self._calc_comp_label(self.comp_aggr_1)

    @rx.var
    def comp_aggr_2(self) -> str:
        prefs = list(self.preferred_competitors)
        return self._calc_comp_aggr(prefs[1] if len(prefs) > 1 else "")

    @rx.var
    def comp_label_2(self) -> str:
        return self._calc_comp_label(self.comp_aggr_2)

    @rx.var
    def comp_aggr_3(self) -> str:
        prefs = list(self.preferred_competitors)
        return self._calc_comp_aggr(prefs[2] if len(prefs) > 2 else "")

    @rx.var
    def comp_label_3(self) -> str:
        return self._calc_comp_label(self.comp_aggr_3)

    @rx.var
    def comp_aggr_4(self) -> str:
        prefs = list(self.preferred_competitors)
        return self._calc_comp_aggr(prefs[3] if len(prefs) > 3 else "")

    @rx.var
    def comp_label_4(self) -> str:
        return self._calc_comp_label(self.comp_aggr_4)

    @rx.var
    def comp_aggr_5(self) -> str:
        prefs = list(self.preferred_competitors)
        return self._calc_comp_aggr(prefs[4] if len(prefs) > 4 else "")

    @rx.var
    def comp_label_5(self) -> str:
        return self._calc_comp_label(self.comp_aggr_5)

    def _calc_comp_aggr(self, comp_name: str) -> str:
        if not comp_name:
            return "N/D"
        import datetime
        from sqlmodel import Session, select
        from database import CompetitorOffer, Product, engine
        today = datetime.date.today()
        pairs = []
        with Session(engine) as session:
            offers = session.exec(
                select(CompetitorOffer, Product)
                .join(Product, Product.id == CompetitorOffer.product_id)
                .where(
                    CompetitorOffer.merchant_name == comp_name,
                    CompetitorOffer.snapshot_date == today,
                    CompetitorOffer.price > 0,
                    Product.my_price > 0,
                )
            ).all()
            for offer, product in offers:
                if offer.price >= product.my_price * 0.5:
                    pairs.append((product.my_price, offer.price))
        if not pairs:
            return "N/D"
        avg_delta = sum((cp - mp) / mp * 100 for mp, cp in pairs) / len(pairs)
        sign = "+" if avg_delta >= 0 else ""
        return f"{sign}{avg_delta:.1f}%"

    def _calc_comp_label(self, aggr: str) -> str:
        if aggr == "N/D":
            return "→ nessun dato"
        if aggr in ("0.0%", "+0.0%"):
            return "→ allineato"
        return "↓ più economico di te" if aggr.startswith("-") else "↑ più caro di te"

    # ---------------------------------------------------------------------------
    # COMPUTED VARS — TABELLA HOME
    # ---------------------------------------------------------------------------

    @rx.var
    def filtered_product_list(self) -> List[Dict[str, Any]]:
        products = list(self._products_raw)

        if self.search_product:
            q = self.search_product.lower()
            products = [p for p in products if q in p["name"].lower() or q in p["sku"].lower()]

        if self.filter_brand != "Tutti":
            products = [p for p in products if p["brand"] == self.filter_brand]

        if self.filter_category != "Tutte":
            products = [p for p in products if p["category"] == self.filter_category]

        active_comps = list(self.filter_competitor)
        if active_comps:
            filtered = []
            for p in products:
                # Trova il prezzo minimo tra i competitor selezionati
                comp_prices = []
                best_comp_name = None
                best_comp_price = None
                for comp_name in active_comps:
                    price = None
                    if p["comp_1_name"] == comp_name:
                        try:
                            price = float(p["comp_1_price"])
                        except (ValueError, TypeError):
                            pass
                    elif p["comp_2_name"] == comp_name:
                        try:
                            price = float(p["comp_2_price"])
                        except (ValueError, TypeError):
                            pass
                    if price is not None:
                        comp_prices.append((comp_name, price))

                if not comp_prices:
                    continue  # prodotto non ha nessuno dei competitor selezionati

                # Prendi il più economico tra i selezionati
                best_comp_name, best_comp_price = min(comp_prices, key=lambda x: x[1])

                # Ricalcola PI rispetto al min dei competitor selezionati
                if best_comp_price > 0 and p["my_price"] > 0:
                    pi_comp = round((p["my_price"] / best_comp_price) * 100, 1)
                else:
                    pi_comp = p["price_index"]

                p = dict(p)
                p["price_index"] = pi_comp
                p["price_index_fmt"] = f"{pi_comp:.1f}"
                p["pi_color"] = "red" if pi_comp > 110 else ("orange" if pi_comp > 103 else "green")
                p["min_comp_name"] = best_comp_name
                p["min_comp_price_fmt"] = f"€{best_comp_price:.2f}"
                filtered.append(p)
            products = filtered

        col = self.sort_column
        if col in ("price_index", "my_price", "min_price", "my_rank", "nb_merchants", "popularity"):
            products = sorted(products, key=lambda p: p.get(col, 0), reverse=self.sort_reverse)
        else:
            products = sorted(products, key=lambda p: str(p.get(col, "")), reverse=self.sort_reverse)

        start = (self.page_number - 1) * self.items_per_page
        return products[start: start + self.items_per_page]

    @rx.var
    def total_filtered(self) -> int:
        products = list(self._products_raw)
        if self.search_product:
            q = self.search_product.lower()
            products = [p for p in products if q in p["name"].lower() or q in p["sku"].lower()]
        if self.filter_brand != "Tutti":
            products = [p for p in products if p["brand"] == self.filter_brand]
        if self.filter_category != "Tutte":
            products = [p for p in products if p["category"] == self.filter_category]
        return len(products)

    @rx.var
    def total_pages(self) -> int:
        total = self.total_filtered
        if total == 0:
            return 1
        return (total // self.items_per_page) + (1 if total % self.items_per_page > 0 else 0)

    # ---------------------------------------------------------------------------
    # COMPUTED VARS — GRAFICO HOME
    # ---------------------------------------------------------------------------

    @rx.var
    def chart_data(self) -> List[Dict[str, Any]]:
        return list(self._chart_data_raw)

    # ---------------------------------------------------------------------------
    # COMPUTED VARS — FILTRI
    # ---------------------------------------------------------------------------

    @rx.var
    def categories(self) -> List[str]:
        return list(self._categories_raw) if self._categories_raw else ["Tutte"]

    @rx.var
    def brands(self) -> List[str]:
        return list(self._brands_raw) if self._brands_raw else ["Tutti"]

    @rx.var
    def competitors(self) -> List[str]:
        return list(self._merchants_raw) if self._merchants_raw else []

    # ---------------------------------------------------------------------------
    # COMPUTED VARS — DETAILS
    # ---------------------------------------------------------------------------

    @rx.var
    def selected_product_name(self) -> str:
        return self._selected_product.get("name", "Prodotto non trovato")

    @rx.var
    def selected_product_brand(self) -> str:
        return self._selected_product.get("brand", "-")

    @rx.var
    def selected_product_category(self) -> str:
        return self._selected_product.get("category", "-")

    @rx.var
    def selected_product_sku(self) -> str:
        return self.selected_sku or "-"

    @rx.var
    def selected_product_price(self) -> str:
        return self._selected_product.get("price", "0.00")

    @rx.var
    def selected_product_pos(self) -> str:
        return self._selected_product.get("pos", "#-")

    @rx.var
    def selected_product_pos_color(self) -> str:
        return self._selected_product.get("pos_color", "gray")

    @rx.var
    def selected_product_revenue(self) -> str:
        sku = self.selected_sku
        if sku and sku in self._ga4_data:
            return f"{self._ga4_data[sku].get('revenue', 0):.2f}"
        return "N/D"

    @rx.var
    def selected_product_units(self) -> str:
        sku = self.selected_sku
        if sku and sku in self._ga4_data:
            return str(self._ga4_data[sku].get("transactions", 0))
        return "N/D"

    @rx.var
    def selected_price_index_label(self) -> str:
        return self._selected_product.get("price_index_label", "N/D")

    @rx.var
    def selected_price_index_color(self) -> str:
        return self._selected_product.get("price_index_color", "#64748B")

    @rx.var
    def suggested_price(self) -> str:
        return self._selected_product.get("suggested_price", "N/D")

    @rx.var
    def selected_competitors(self) -> List[Dict[str, Any]]:
        return list(self._selected_competitors)

    @rx.var
    def positioning_history(self) -> List[Dict[str, Any]]:
        return list(self._selected_positioning_history)

    @rx.var
    def price_history_chart(self) -> List[Dict[str, Any]]:
        return list(self._selected_price_history)

    @rx.var
    def selected_repricing_rules(self) -> List[Dict[str, Any]]:
        return [
            {"label": "Rimani sotto il competitor #1 di €0.01", "status": "Attiva", "status_color": "green"},
            {"label": "Non scendere sotto costo acquisto + 15%", "status": "Attiva", "status_color": "green"},
            {"label": "Match automatico se perdi posizione #1", "status": "In pausa", "status_color": "orange"},
        ]

    # ---------------------------------------------------------------------------
    # EVENTI
    # ---------------------------------------------------------------------------

    @rx.event
    def set_search_product(self, v: str):
        self.search_product = v
        self.page_number = 1

    @rx.event
    def set_filter_brand(self, v: str):
        self.filter_brand = v
        self.page_number = 1

    @rx.event
    def set_filter_category(self, v: str):
        self.filter_category = v
        self.page_number = 1

    @rx.event
    def set_filter_competitor(self, v: str):
        """Toggle singolo competitor on/off."""
        if v == "Tutti" or v == "":
            self.filter_competitor = []
        elif v in self.filter_competitor:
            self.filter_competitor = [c for c in self.filter_competitor if c != v]
        else:
            self.filter_competitor = list(self.filter_competitor) + [v]
        self.page_number = 1

    @rx.event
    def select_competitor_filter(self, name: str):
        """Toggle competitor dalla card KPI."""
        if name in self.filter_competitor:
            self.filter_competitor = [c for c in self.filter_competitor if c != name]
        else:
            self.filter_competitor = list(self.filter_competitor) + [name]
        self.page_number = 1

    @rx.event
    def toggle_sort(self, column: str):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.page_number = 1

    @rx.event
    def prev_page(self):
        if self.page_number > 1:
            self.page_number -= 1

    @rx.event
    def next_page(self):
        if self.page_number < self.total_pages:
            self.page_number += 1

    @rx.event
    def nav_to_brand(self, brand: str):
        self.filter_brand = brand
        self.page_number = 1
        return rx.redirect("/brand")

    @rx.event
    def nav_to_product_detail(self, sku: str):
        self.selected_sku = sku
        self._load_product_detail()
        return rx.redirect("/dettaglio")

    @rx.event
    def set_comp_box_1(self, v: str): self.comp_box_1 = v
    @rx.event
    def set_comp_box_2(self, v: str): self.comp_box_2 = v
    @rx.event
    def set_comp_box_3(self, v: str): self.comp_box_3 = v

    def set_pref_comp_0(self, v: str): self._set_pref(0, v)
    def set_pref_comp_1(self, v: str): self._set_pref(1, v)
    def set_pref_comp_2(self, v: str): self._set_pref(2, v)
    def set_pref_comp_3(self, v: str): self._set_pref(3, v)
    def set_pref_comp_4(self, v: str): self._set_pref(4, v)

    def _set_pref(self, index: int, value: str):
        updated = list(self.preferred_competitors)
        while len(updated) < 5:
            updated.append("")
        updated[index] = "" if value == "__none__" else value
        self.preferred_competitors = updated

    @rx.event
    def set_ga4_property_id(self, v: str): self.ga4_property_id = v

    @rx.event
    def set_ga4_json_key(self, v: str): self.ga4_json_key = v

    @rx.event
    def save_ga4_config(self):
        if self.ga4_property_id:
            self.ga4_status = "Configurato ✅"
            return rx.toast("Configurazione salvata!")
        return rx.toast("Property ID mancante!")

    @rx.event(background=True)
    async def connect_ga4(self, files: list):
        """Salva il file JSON delle credenziali GA4."""
        import aiofiles
        async with self:
            self.ga4_status = "Salvataggio credenziali..."
        try:
            if not files:
                async with self:
                    self.ga4_status = "Errore: nessun file caricato"
                return
            file = files[0]
            creds_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "ga4_credentials.json"
            )
            async with aiofiles.open(creds_path, "wb") as f:
                await f.write(file)
            async with self:
                self.ga4_status = "Connesso ✅"
        except Exception as e:
            async with self:
                self.ga4_status = f"Errore: {str(e)[:80]}"

    @rx.event(background=True)
    async def sync_ga4_revenue(self):
        async with self:
            if not self.ga4_property_id:
                self.ga4_status = "Errore: Property ID mancante"
                return
            self.is_syncing_ga4 = True
            self.ga4_status = "Sync GA4 in corso..."
        try:
            creds_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "ga4_credentials.json"
            )
            if not os.path.exists(creds_path):
                async with self:
                    self.ga4_status = "Errore: credenziali non caricate"
                    self.is_syncing_ga4 = False
                return

            from services.ga4_service import fetch_revenue_by_sku
            data = await asyncio.get_event_loop().run_in_executor(
                None, fetch_revenue_by_sku, creds_path, self.ga4_property_id
            )
            async with self:
                self._ga4_data = data
                self.last_sync_ga4 = datetime.datetime.now().strftime("%d/%m %H:%M")
                self.ga4_status = f"Connesso ✅ ({len(data)} SKU)"
        except Exception as e:
            async with self:
                self.ga4_status = f"Errore: {str(e)[:80]}"
        finally:
            async with self:
                self.is_syncing_ga4 = False

    @rx.event(background=True)
    async def sync_prices(self):
        """Lancia la sync AlphaPosition in background."""
        async with self:
            self.is_syncing = True
            self.sync_status = "Avvio sync AlphaPosition..."
            self.sync_progress = 0

        try:
            import subprocess
            result = subprocess.run(
                ["python", "-c",
                 "from services.alphaposition_fetcher import run_daily_sync; r = run_daily_sync(); print(r)"],
                capture_output=True, text=True, timeout=300,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            async with self:
                if result.returncode == 0:
                    self.sync_status = "✅ Sync completata"
                    self.sync_progress = 100
                    self._load_data()
                else:
                    self.sync_status = f"❌ Errore: {result.stderr[:100]}"
        except Exception as e:
            async with self:
                self.sync_status = f"❌ {str(e)[:100]}"
        finally:
            async with self:
                self.is_syncing = False
                self.sync_current_product = ""

    @rx.event
    def import_sensation_data(self):
        return rx.toast("Usa la sync AlphaPosition per caricare dati reali.")

    # ---------------------------------------------------------------------------
    # VARIABILI E METODI PER filters.py
    # ---------------------------------------------------------------------------
    start_date: str = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    end_date: str = datetime.date.today().isoformat()
    compare_mode: bool = False

    @rx.var
    def previous_period_label(self) -> str:
        try:
            start = datetime.date.fromisoformat(self.start_date)
            end = datetime.date.fromisoformat(self.end_date)
            delta = (end - start).days + 1
            ps = start - datetime.timedelta(days=delta)
            pe = start - datetime.timedelta(days=1)
            return f"Confronto: {ps.strftime('%d %b')} - {pe.strftime('%d %b %Y')}"
        except Exception:
            return "Date non valide"

    @rx.event
    def set_start_date(self, v: str): self.start_date = v

    @rx.event
    def set_end_date(self, v: str): self.end_date = v

    @rx.event
    def set_compare_mode(self, v: bool): self.compare_mode = v

    @rx.event
    def toggle_brand(self, name: str):
        self.filter_brand = "Tutti" if name == "Tutti" else name
        self.page_number = 1

    @rx.event
    def toggle_competitor(self, name: str):
        if name == "Tutti" or name == "":
            self.filter_competitor = []
        elif name in self.filter_competitor:
            self.filter_competitor = [c for c in self.filter_competitor if c != name]
        else:
            self.filter_competitor = list(self.filter_competitor) + [name]
        self.page_number = 1