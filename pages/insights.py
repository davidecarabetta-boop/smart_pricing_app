import reflex as rx
# Importiamo solo quello che serve dal file centrale
from ..state import State
from ..state import State, PriceRecord


def insight_stat_card(label: str, value: str, icon: str, color: str):
    """Mini card per statistiche rapide in Insights."""
    return rx.card(
        rx.hstack(
            rx.center(
                rx.icon(tag=icon, size=20, color="white"),
                bg=color,
                border_radius="lg",
                padding="3",
            ),
            rx.vstack(
                rx.text(label, size="1", color="gray", weight="medium"),
                rx.text(value, size="4", weight="bold"),
                spacing="0",
                align_items="start",
            ),
            spacing="3",
            align="center",
        ),
        variant="surface",
        width="100%",
    )


def insights() -> rx.Component:
    """Pagina Insights: Visualizzazione dati strategici e trend."""
    return rx.vstack(
        # Qui potresti avere la tua navbar se non è globale
        rx.box(
            rx.vstack(
                rx.heading("Analytics & Market Insights", size="7", weight="bold"),
                rx.text("Analisi approfondita del posizionamento e delle opportunità di margine.", color="gray"),

                # 1. GRID STATISTICHE RAPIDE
                rx.grid(
                    insight_stat_card("Target Price Index", "100.0", "target", "blue"),
                    insight_stat_card("Prodotti Monitorati", f"{State.total_pages * 100}", "layers", "purple"),
                    # Nel file insights.py, dentro la funzione insight_stat_card
                    insight_stat_card("Rischio Critico", f"{State.critical_risk}", "triangle-alert", "red"),
                    columns=rx.breakpoints(initial="1", sm="2", lg="3"),
                    spacing="4",
                    width="100%",
                ),

                # 2. GRAFICO TREND (Usa i dati aggregati dallo State)
                rx.vstack(
                    rx.heading("Market Gap Analysis", size="4", weight="bold"),
                    rx.text("Differenza percentuale media tra il tuo prezzo e il miglior competitor.", size="2",
                            color="gray"),
                    rx.recharts.area_chart(
                        rx.recharts.area(
                            data_key="market",
                            stroke="#94A3B8",
                            fill="#F1F5F9",
                            name="Media Mercato"
                        ),
                        rx.recharts.area(
                            data_key="price",
                            stroke="#3B82F6",
                            fill="#DBEAFE",
                            name="Il Mio Prezzo"
                        ),
                        rx.recharts.x_axis(data_key="name"),
                        rx.recharts.y_axis(),
                        rx.recharts.legend(),
                        rx.recharts.graphing_tooltip(),
                        data=State.chart_data,
                        width="100%",
                        height=400,
                    ),
                    bg="white",
                    padding="2rem",
                    border_radius="20px",
                    box_shadow="sm",
                    width="100%",
                    align_items="start",
                ),

                # 3. ANALISI OPPORTUNITÀ
                rx.link(
                    rx.hstack(
                        rx.icon(tag="sparkles", color="#EAB308"),
                        rx.text(f"Hai un'opportunità di margine di {State.margin_opp} sui prodotti in Rank #1.",
                                weight="medium"),
                        rx.spacer(),
                        rx.icon(tag="arrow-right"),
                        width="100%",
                        padding="1.5rem",
                        bg="yellow.50",
                        border="1px solid #FEF08A",
                        border_radius="16px",
                        color="yellow.900",
                    ),
                    href="/repricing_analysis",
                    text_decoration="none",
                    width="100%",
                ),

                spacing="7",
                width="100%",
            ),
            width="100%",
            padding="2rem",
        ),
        width="100%",
        bg="#F8FAFC",
        min_height="100vh",
    )