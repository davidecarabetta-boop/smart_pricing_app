import pandas as pd
from typing import List, Dict

class PriceIntelligence:
    def __init__(self):
        # Qui in futuro inizializzerai i client API
        self.raw_data = None

    def get_market_snapshot(self) -> pd.DataFrame:
        """Simula l'unione di Trovaprezzi + DataForSEO"""
        data = {
            "sku": ["SAUV-100", "CHAN-50", "DIOR-60"],
            "my_price": [115.0, 85.0, 95.0],
            "competitor_low": [109.0, 88.0, 92.0],
            "source": ["Trovaprezzi", "DataForSEO", "Trovaprezzi"]
        }
        return pd.DataFrame(data)

    def get_ga4_metrics(self) -> pd.DataFrame:
        """Simula i dati di vendita da GA4"""
        data = {
            "sku": ["SAUV-100", "CHAN-50", "DIOR-60"],
            "sessions": [1200, 850, 400],
            "conversions": [12, 45, 2]
        }
        return pd.DataFrame(data)

    def get_smart_analysis(self, row_data: Dict):
        """Qui chiamerai Gemini API per avere il suggerimento"""
        # Esempio di prompt: "Il prezzo è il 5% più alto del market ma le conversioni calano. Cosa faccio?"
        return "Abbassa a €112 per recuperare il 15% di click share."