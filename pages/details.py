import reflex as rx
from ..state import State
from ..components.navbar import navbar

def detail_kpi(label: str, value: str, color: str):
    return rx.vstack(
        rx.text(label, size="2", color="gray", weight="medium"),
        rx.heading(value, size="6", weight="bold", color=color),
        padding="1rem",
        bg="white",
        border_radius="12px",
        box_shadow="sm",
        width="100%",
        align_items="start",
    )

def critical_product_row(prod: dict):
    return rx.table.row(
        rx.table.cell(rx.text(prod["name"], weight="bold")),
        rx.table.cell(f"€{prod['price']}"),
        rx.table.cell(rx.text(prod["comp"], color="red")),
        rx.table.cell(
            rx.badge("Overpriced", color_scheme="red", variant="soft")
        ),
        rx.table.cell(
            rx.button("Fix", size="1", color_scheme="blue", variant="outline")
        ),
    )

# CAMBIATO NOME QUI: Da pagina_dettaglio a details
def details() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.box(
            rx.vstack(
                # INTESTAZIONE
                rx.hstack(
                    rx.button(
                        rx.icon(tag="arrow-left"),
                        on_click=rx.redirect("/"),
                        variant="ghost",
                        color_scheme="gray"
                    ),
                    rx.vstack(
                        rx.heading("Analisi SKU Critiche", size="7"),
                        rx.text("Focus sugli 8 prodotti con Price Index > 110", color="gray"),
                        align_items="start",
                        spacing="0",
                    ),
                    width="100%",
                    spacing="4",
                    align="center",
                ),

                # RIGA KPI
                rx.grid(
                    detail_kpi("Impatto Volume", "-18.5%", "red"),
                    detail_kpi("Loss Revenue", "€450/sett", "red"),
                    detail_kpi("Avg Competitor", "€89.40", "gray"),
                    detail_kpi("Target Price", "€92.00", "green"),
                    columns=rx.breakpoints(initial="1", sm="2", lg="4"),
                    spacing="4",
                    width="100%",
                ),

                # GRAFICO
                rx.vstack(
                    rx.heading("Gap di Prezzo vs Top 3 Competitor", size="4"),
                    rx.recharts.bar_chart(
                        rx.recharts.bar(
                            data_key="price", fill="#EF4444", name="Tuo Prezzo", radius=[4, 4, 0, 0]
                        ),
                        rx.recharts.bar(
                            data_key="market", fill="#94A3B8", name="Media Mercato", radius=[4, 4, 0, 0]
                        ),
                        rx.recharts.x_axis(data_key="name"),
                        rx.recharts.y_axis(),
                        rx.recharts.legend(),
                        rx.recharts.graphing_tooltip(),
                        data=State.chart_data,
                        width="100%",
                        height=300,
                    ),
                    bg="white", padding="1.5rem", border_radius="16px", width="100%",
                ),

                # TABELLA
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("PRODOTTO"),
                                rx.table.column_header_cell("TUO PREZZO"),
                                rx.table.column_header_cell("MIGLIOR COMP."),
                                rx.table.column_header_cell("STATUS"),
                                rx.table.column_header_cell("AZIONE"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(State.product_list, critical_product_row)
                        ),
                        width="100%",
                    ),
                    bg="white", padding="1.5rem", border_radius="16px", width="100%",
                ),
                spacing="6",
                width="100%",
                align_items="stretch",
            ),
            width="100%",
            padding_x="2%",
            padding_y="2rem",
        ),
        bg="#EDF2F7",
        min_height="100vh",
        width="100%",
        spacing="0",
    )