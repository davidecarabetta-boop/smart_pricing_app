import pandas as pd


def get_real_market_data() -> list[dict]:
    """
    Simula l'estrazione dati dal DB e prepara i calcoli per Reflex.
    In futuro qui metteremo: pd.read_csv("tuo_file.csv") o la query SQL.
    """
    # 1. I tuoi dati grezzi (come se venissero da un database)
    raw_data = {
        "sku": ["D001", "A002", "C003"],
        "name": ["Sauvage EDP 100ml", "Acqua di Giò 50ml", "Bleu de Chanel 100ml"],
        "brand": ["Dior", "Armani", "Chanel"],
        "my_price": [115.00, 75.00, 135.00],
        "stock": ["Alto", "Medio", "Basso"],
        "comp_notino": [109.00, 79.00, 130.00],
        "comp_douglas": [115.00, 75.00, 140.00]
    }

    df = pd.DataFrame(raw_data)

    # 2. Calcoli di Business Logic vettorializzati (molto più veloci)
    # Calcoliamo il competitor più basso per ogni riga
    df['min_market'] = df[['comp_notino', 'comp_douglas']].min(axis=1)

    # Calcoliamo il posizionamento percentuale rispetto al mercato
    df['positioning_pct'] = ((df['my_price'] - df['min_market']) / df['min_market'] * 100).round(1)

    # Generiamo dinamicamente la stringa del Positioning (es. "+5.5%")
    df['positioning'] = df['positioning_pct'].apply(
        lambda x: f"+{x}%" if x > 0 else (f"{x}%" if x < 0 else "Allineato")
    )

    # Assegniamo una strategia base
    df['strategy'] = df.apply(
        lambda row: "Margin Protection" if row['my_price'] <= row['min_market'] else "Match Lowest",
        axis=1
    )

    # Generiamo un SVG finto per la sparkline per ogni prodotto
    df[
        'trend_svg'] = '<svg width="80" height="30" viewBox="0 0 100 40"><polyline points="0,20 20,25 40,15 60,10 80,18" fill="none" stroke="#1A73E8" stroke-width="2" /></svg>'

    # Convertiamo in dizionario per mandarlo alla UI
    return df.to_dict('records')