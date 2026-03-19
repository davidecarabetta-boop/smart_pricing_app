import reflex as rx
from typing import Dict, Any
from ..state import State
from ..components.navbar import navbar
from ..components.filters import global_filter_bar

# --- COMPONENTI RIUTILIZZABILI ---

def kpi_card(title: str, value: str, footer: str, footer_color: str, help_text: str, url: str = "#") -> rx.Component:
    return rx.link(
        rx.vstack(
            rx.hstack(
                rx.text(title, size="2", color="gray", weight="medium"),
                rx.tooltip(
                    rx.icon(tag="circle-help", size=14, color="#94A3B8"),
                    content=help_text,
                ),
                align="center",
                spacing="2",
            ),
            rx.heading(value, size="7", weight="bold"),
            rx.badge(footer, color_scheme=footer_color, variant="soft", radius="full"),
            padding="1.25rem",
            bg="white",
            border_radius="16px",
            box_shadow="0 1px 3px rgba(0,0,0,0.1)",
            width="100%",
            align_items="start",
            spacing="2",
            transition="all 0.2s ease",
            _hover={
                "box_shadow": "0 4px 12px rgba(0,0,0,0.1)",
                "transform": "translateY(-2px)",
                "border": "1px solid #3B82F6",
            },
        ),
        href=url,
        text_decoration="none",
        width="100%",
    )

def product_row(prod: Dict[str, Any]) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(prod["name"], weight="bold")),
        rx.table.cell(f"€{prod['price']}"),
        rx.table.cell(rx.text(prod["comp"], color="gray")),
        rx.table.cell(rx.badge(prod["pos"], color_scheme=prod["color"])),
    )

# --- PAGINA HOME INTEGRALE ---

def home() -> rx.Component:
    return rx.vstack(
        # 1. NAVBAR FISSA IN ALTO
        navbar(),

        # 2. CONTENITORE PRINCIPALE
        rx.box(
            rx.vstack(
                # BARRA FILTRI GLOBALE
                global_filter_bar(),

                # SEZIONE KPI (GRIGLIA REATTIVA)
                rx.grid(
                    kpi_card(
                        "Price Index", f"{State.price_index}", State.pi_status, State.pi_color,
                        "Indice medio di posizionamento: 100 è l'allineamento perfetto col mercato."
                    ),
                    kpi_card(
                        "Win Rate", State.win_rate, "Prodotti Rank #1", "blue",
                        "Percentuale di prodotti nel tuo catalogo che hanno il prezzo più basso assoluto."
                    ),
                    kpi_card(
                        "Profit Opportunity", State.margin_opp, "Margine dormiente", "green",
                        "Soldi recuperabili alzando i prezzi senza perdere la posizione di vantaggio."
                    ),
                    kpi_card(
                        "Critical Risk", f"{State.critical_risk} SKU", "Fuori mercato", State.risk_color,
                        "Prodotti con prezzo troppo alto rispetto ai competitor. Clicca per i dettagli.",
                        url="/dettaglio"
                    ),
                    columns=rx.breakpoints(initial="1", sm="2", lg="4"),
                    spacing="4",
                    width="100%",
                ),

                # --- SEZIONE SMART ACTION (Sistemata virgola e identazione) ---
                rx.link(
                    rx.hstack(
                        rx.vstack(
                            rx.hstack(
                                rx.icon(tag="zap", color="#EAB308", size=20),
                                rx.heading("Suggerimento Strategico", size="3", weight="bold"),
                                align="center"
                            ),
                            rx.text(
                                f"Puoi recuperare {State.margin_opp} alzando il prezzo su 12 prodotti. Clicca per vedere il confronto con i competitor.",
                                size="2", color="gray"
                            ),
                            align_items="start",
                            spacing="1",
                        ),
                        rx.spacer(),
                        rx.button("Analizza e Applica", variant="solid", color_scheme="blue", size="3"),
                        width="100%",
                        bg="white",
                        padding="1.5rem",
                        border_radius="16px",
                        border="1px solid #E2E8F0",
                        align="center",
                        transition="all 0.2s ease",
                        _hover={"border": "1px solid #3B82F6", "box_shadow": "sm"},
                    ),
                    href="/repricing_analysis",
                    text_decoration="none",
                    width="100%",
                ), # <--- AGGIUNTA VIRGOLA MANCANTE QUI

                # SEZIONE GRAFICO (AREA CHART RECHART)
                rx.vstack(
                    rx.heading("Andamento Posizionamento Prezzi", size="4", weight="bold"),
                    rx.recharts.area_chart(
                        rx.recharts.area(data_key="price", stroke="#2563EB", fill="#DBEAFE", name="Il mio Prezzo"),
                        rx.recharts.area(data_key="market", stroke="#94A3B8", fill="#F1F5F9", name="Media Mercato"),
                        rx.recharts.x_axis(data_key="name"),
                        rx.recharts.y_axis(),
                        rx.recharts.legend(),
                        rx.recharts.graphing_tooltip(),
                        data=State.chart_data,
                        width="100%",
                        height=350,
                    ),
                    bg="white", padding="1.5rem", border_radius="16px", box_shadow="sm",
                    width="100%", align_items="start",
                ),

                # SEZIONE TABELLA DETTAGLIO
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("PRODOTTO"),
                                rx.table.column_header_cell("MY PRICE"),
                                rx.table.column_header_cell("COMPETITORS"),
                                rx.table.column_header_cell("POSITIONING"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(State.filtered_product_list, product_row)
                        ),
                        width="100%",
                    ),
                    bg="white", padding="1.5rem", border_radius="16px", border="1px solid #F0F0F0", width="100%",
                ),
                spacing="6",
                width="100%",
                align_items="stretch", #
            ),
            width="100%",
            padding_x="1.5%", #
            padding_y="2rem",
        ),
        bg="#EDF2F7", #
        min_height="100vh",
        width="100%",
        spacing="0",
    )