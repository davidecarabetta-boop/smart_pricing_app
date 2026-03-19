import reflex as rx
from ..state import State
from ..components.navbar import navbar
from ..components.filters import global_filter_bar

def history_row(item):
    return rx.table.row(rx.table.cell(item["date"]), rx.table.cell(rx.text(item["sku"], weight="bold")), rx.table.cell(f"€{item['old']}"), rx.table.cell(f"€{item['new']}"), rx.table.cell(rx.badge(item["var"], color_scheme=item["color"], variant="solid")))

def history():
    return rx.vstack(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Cronologia", size="8"),
                global_filter_bar(),
                rx.box(rx.table.root(rx.table.header(rx.table.row(rx.table.column_header_cell("DATA"), rx.table.column_header_cell("SKU"), rx.table.column_header_cell("OLD"), rx.table.column_header_cell("NEW"), rx.table.column_header_cell("VAR"))), rx.table.body(rx.foreach(State.history_list, history_row)), width="100%"), bg="white", padding="1.5rem", border_radius="16px", width="100%"),
                width="100%", spacing="6", padding_y="2rem",
            ),
        ),
        bg="#F8FAFC", min_height="100vh",
    )