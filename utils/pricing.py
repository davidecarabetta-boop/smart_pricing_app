def calculate_price_index(my_price: float, comp_prices: list[float]) -> float:
    """
    Calcola il Price Index rispetto alla media dei competitor.
    Un valore > 100 significa che sei più caro della media.
    """
    if not comp_prices:
        return 100.0
    avg_comp = sum(comp_prices) / len(comp_prices)
    return round((my_price / avg_comp) * 100, 1)