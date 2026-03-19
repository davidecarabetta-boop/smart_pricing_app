import reflex as rx
from typing import List, Dict, Any

class State(rx.State):
    # --- 1. KPI UNIVERSALI (Impatto Immediato) ---
    price_index: float = 101.5       # Indice di posizionamento medio
    win_rate: str = "42%"            # % di prodotti dove siamo i più economici
    margin_opp: str = "€1.2k"        # Margine recuperabile (ex margin_recovery)
    critical_risk: int = 8           # SKU con prezzo troppo alto rispetto al mercato

    # --- 2. VARIABILI BASE E FILTRI ---
    sensitivity: int = 50
    target_price: float = 115.00
    filter_brand: str = "Tutti"
    filter_category: str = "Tutte"
    filter_time: str = "Tutto"
    search_product: str = ""

    brands: List[str] = ["Tutti", "Dior", "Chanel", "Armani", "Versace"]
    categories: List[str] = ["Tutte", "Profumi Uomo", "Profumi Donna", "Make-up"]
    time_options: List[str] = ["Tutto", "Oggi", "Ultimi 7 giorni", "Ultimo mese"]

    # --- 3. DATI PER LE PAGINE (Mock Data) ---
    state_competitors: List[Dict[str, Any]] = [
        {"name": "Notino", "diff": -12, "status": "vs you", "color": "red"},
        {"name": "Sephora", "diff": 3, "status": "vs you", "color": "green"},
        {"name": "Douglas", "diff": 0, "status": "Allineato", "color": "gray"},
    ]

    product_list: List[Dict[str, Any]] = [
        {"name": "Sauvage EDP 100ml", "brand": "Dior", "cat": "Profumi Uomo", "price": 104.50, "comp": "Not: 109.0", "pos": "+5.5%", "color": "orange"},
        {"name": "Bleu de Chanel 50ml", "brand": "Chanel", "cat": "Profumi Uomo", "price": 85.00, "comp": "Amz: 82.0", "pos": "-3.5%", "color": "red"},
        {"name": "Acqua di Gio 100ml", "brand": "Armani", "cat": "Profumi Uomo", "price": 92.00, "comp": "Dou: 95.0", "pos": "+3.2%", "color": "green"},
        {"name": "Eros Flame 100ml", "brand": "Versace", "cat": "Profumi Uomo", "price": 65.00, "comp": "Sep: 68.0", "pos": "+4.6%", "color": "green"},
    ]

    chart_data: List[Dict[str, Any]] = [
        {"name": "Lun", "price": 95, "market": 98}, {"name": "Mar", "price": 94, "market": 97},
        {"name": "Mer", "price": 97, "market": 96}, {"name": "Gio", "price": 96, "market": 95},
        {"name": "Ven", "price": 92, "market": 94}, {"name": "Sab", "price": 93, "market": 93},
        {"name": "Dom", "price": 94, "market": 92},
    ]

    # NUOVI DATI PER ANALISI REPRICING (Pagina di confronto a 5 competitor)
    repricing_analysis_list: List[Dict[str, Any]] = [
        {"name": "Sauvage EDP 100ml", "new_price": 102.50, "c1": 109.0, "c2": 105.0, "c3": 110.0, "c4": 108.5, "c5": 112.0},
        {"name": "Bleu de Chanel 50ml", "new_price": 84.00, "c1": 82.0, "c2": 85.0, "c3": 86.0, "c4": 84.5, "c5": 88.0},
        {"name": "Acqua di Gio 100ml", "new_price": 94.20, "c1": 95.0, "c2": 96.0, "c3": 94.5, "c4": 98.0, "c5": 95.5},
    ]

    category_data: List[Dict[str, Any]] = [
        {"name": "Profumi Uomo", "value": 45, "fill": "#2563EB"},
        {"name": "Profumi Donna", "value": 30, "fill": "#EC4899"},
        {"name": "Make-up", "value": 15, "fill": "#8B5CF6"},
    ]

    market_position_data: List[Dict[str, Any]] = [
        {"name": "Amazon", "price": 98}, {"name": "Notino", "price": 105},
        {"name": "Douglas", "price": 92}, {"name": "Sephora", "price": 110},
    ]

    history_list: List[Dict[str, Any]] = [
        {"date": "2024-05-20 14:30", "sku": "Sauvage 100ml", "old": "100.00", "new": "105.50", "var": "+5.5%", "color": "green"},
        {"date": "2024-05-20 12:15", "sku": "Eros Flame 100ml", "old": "68.00", "new": "65.00", "var": "-4.4%", "color": "red"},
    ]

    # --- 4. SETTERS ESPLICITI (Previene i warning di image_8b059b) ---
    def set_filter_brand(self, val: str): self.filter_brand = val
    def set_filter_category(self, val: str): self.filter_category = val
    def set_filter_time(self, val: str): self.filter_time = val
    def set_search_product(self, val: str): self.search_product = val
    def set_sensitivity(self, val: List[float]):
        if val: self.sensitivity = int(val[0])

    # --- 5. VARIABILI COMPUTATE (@rx.var) ---
    @rx.var
    def filtered_product_list(self) -> List[Dict[str, Any]]:
        filtered = self.product_list
        if self.filter_brand != "Tutti":
            filtered = [p for p in filtered if p["brand"] == self.filter_brand]
        if self.filter_category != "Tutte":
            filtered = [p for p in filtered if p["cat"] == self.filter_category]
        if self.search_product != "":
            filtered = [p for p in filtered if self.search_product.lower() in p["name"].lower()]
        return filtered

    @rx.var
    def pi_status(self) -> str:
        return "High" if self.price_index > 100 else "Optimal"

    @rx.var
    def pi_color(self) -> str:
        return "red" if self.price_index > 100 else "green"

    @rx.var
    def risk_color(self) -> str:
        return "red" if self.critical_risk > 5 else "orange"