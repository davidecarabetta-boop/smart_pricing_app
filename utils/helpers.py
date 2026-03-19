import pandas as pd
import numpy as np


class PricingAnalytics:
    """
    Classe core per il calcolo delle metriche di posizionamento prezzi.
    """

    @staticmethod
    def calculate_price_index(my_price: float, competitor_prices: list) -> float:
        """
        Calcola il Price Index rispetto alla media dei competitor.
        Formula: (Prezzo Mio / Media Competitor) * 100
        Un valore > 100 indica che siamo più cari del mercato.
        """
        valid_prices = [p for p in competitor_prices if p > 0]
        if not valid_prices:
            return 100.0
        avg_competitor = sum(valid_prices) / len(valid_prices)
        return round((my_price / avg_competitor) * 100, 1)

    @staticmethod
    def get_aggressiveness(my_price: float, comp_price: float) -> dict:
        """
        Determina lo scostamento percentuale rispetto a un singolo competitor.
        Ritorna un dizionario con valore, label e colore (CSS).
        """
        if comp_price == 0 or my_price == 0:
            return {"diff": 0, "label": "N/D", "color": "#6c757d"}

        diff_pct = ((comp_price - my_price) / my_price) * 100

        if abs(diff_pct) < 0.5:
            return {"diff": 0, "label": "Allineato", "color": "#34A853", "bg": "#E6F4EA"}
        elif diff_pct < 0:
            return {"diff": round(diff_pct, 1), "label": "vs you", "color": "#EA4335", "bg": "#FCE8E6"}
        else:
            return {"diff": round(diff_pct, 1), "label": "vs you", "color": "#34A853", "bg": "#E6F4EA"}


def format_currency(value):
    return f"€{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")