"""
services/ga4_service.py
Fetch dati revenue da Google Analytics 4 Data API.
Ritorna dict in memoria — niente DB.
"""

from datetime import date, timedelta


def fetch_revenue_by_sku(credentials_path: str, property_id: str, days: int = 30) -> dict:
    """
    Scarica revenue e unità vendute per SKU da GA4.
    Ritorna: {sku: {"revenue": float, "transactions": int}}
    """
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
        from google.oauth2 import service_account
    except ImportError:
        raise ImportError("Installa: pip install google-analytics-data google-auth")

    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    client = BetaAnalyticsDataClient(credentials=credentials)

    if not property_id.startswith("properties/"):
        property_id = f"properties/{property_id}"

    end_date = date.today().strftime("%Y-%m-%d")
    start_date = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")

    request = RunReportRequest(
        property=property_id,
        dimensions=[Dimension(name="itemId")],
        metrics=[
            Metric(name="itemRevenue"),
            Metric(name="itemsPurchased"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )

    response = client.run_report(request)

    results = {}
    for row in response.rows:
        sku = row.dimension_values[0].value
        revenue = float(row.metric_values[0].value or 0)
        transactions = int(float(row.metric_values[1].value or 0))
        results[sku] = {"revenue": revenue, "transactions": transactions}

    return results