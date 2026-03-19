import reflex as rx
from ..state import State
from ..components.navbar import navbar
from ..components.filters import global_filter_bar


def analysis_row(item: dict):
    return rx.table.row(
        rx.table.cell(rx.text(item["name"], weight="bold")),
        rx.table.cell(rx.badge(f"€{item['new_price']}", color_scheme="blue", variant="solid")),
        rx.table.cell(f"€{item['c1']}"),
        rx.table.cell(f"€{item['c2']}"),
        rx.table.cell(f"€{item['c3']}"),
        rx.table.cell(f"€{item['c4']}"),
        rx.table.cell(f"€{item['c5']}"),
    )


def repricing_analysis() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.button(rx.icon(tag="arrow-left"), on_click=rx.redirect("/"), variant="ghost"),
                    rx.heading("Analisi Impatto Repricing Suggerito", size="7"),
                    align="center", spacing="4"
                ),

                global_filter_bar(),  # Manteniamo i filtri per coerenza

                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("PRODOTTO"),
                                rx.table.column_header_cell("TUO NUOVO PREZZO"),
                                rx.table.column_header_cell("COMP 1"),
                                rx.table.column_header_cell("COMP 2"),
                                rx.table.column_header_cell("COMP 3"),
                                rx.table.column_header_cell("COMP 4"),
                                rx.table.column_header_cell("COMP 5"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(State.repricing_analysis_list, analysis_row)
                        ),
                        width="100%",
                    ),
                    bg="white", padding="1.5rem", border_radius="16px", width="100%",
                ),

                rx.hstack(
                    rx.spacer(),
                    rx.button("Annulla", variant="soft", color_scheme="gray"),
                    rx.button("Conferma e Applica a tutti", color_scheme="blue", size="3"),
                    width="100%", spacing="3"
                ),

                spacing="6", width="100%", align_items="stretch",
            ),
            width="100%", padding_x="2%", padding_y="2rem",
        ),
        bg="#EDF2F7", min_height="100vh", width="100%",
    )