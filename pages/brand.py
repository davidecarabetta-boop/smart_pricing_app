import reflex as rx
from typing import Dict, Any
from ..state import State
from ..components.navbar import navbar


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def section_card(*children, **props):
    return rx.box(
        *children,
        bg="white", border_radius="12px", padding="1.25rem 1.5rem",
        border="1px solid #E2E8F0",
        box_shadow="0 1px 2px rgba(0,0,0,0.06)",
        width="100%", **props,
    )


def kpi_box(label: str, value, color: str = "#0F172A"):
    return rx.vstack(
        rx.text(label, size="1", weight="bold", color="#94A3B8",
                letter_spacing="0.06em", text_transform="uppercase"),
        rx.heading(value, size="5", weight="bold", color=color),
        padding="1rem", bg="#F8FAFC", border_radius="10px",
        border="1px solid #E2E8F0", align_items="start", spacing="1",
        width="100%",
    )


def pi_badge(item: dict):
    return rx.badge(
        item["price_index_fmt"],
        color_scheme=rx.cond(
            item["pi_color"] == "red", "red",
            rx.cond(item["pi_color"] == "orange", "orange", "green")
        ),
        variant="soft", radius="full", size="2",
    )


def sort_icon(col: str):
    return rx.cond(
        State.sort_column == col,
        rx.cond(
            State.sort_reverse,
            rx.icon(tag="chevron-down", size=12, color="#3B82F6"),
            rx.icon(tag="chevron-up", size=12, color="#3B82F6"),
        ),
        rx.icon(tag="chevrons-up-down", size=12, color="#CBD5E1"),
    )


def col_header(label: str, col: str):
    return rx.table.column_header_cell(
        rx.hstack(
            rx.text(label, size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
            sort_icon(col),
            spacing="1", align="center", cursor="pointer",
        ),
        on_click=State.toggle_sort(col),
        _hover={"bg": "#F8FAFC"}, cursor="pointer",
    )


def product_row(item: dict):
    return rx.table.row(
        rx.table.cell(
            rx.vstack(
                rx.text(
                    item["name"], weight="medium", color="#1E40AF",
                    cursor="pointer", size="2",
                    _hover={"text_decoration": "underline"},
                    on_click=State.nav_to_product_detail(item["sku"]),
                ),
                rx.badge(item["category"], variant="soft", size="1", color_scheme="blue"),
                spacing="1", align_items="start",
            ),
            padding_y="0.6rem", min_width="220px",
        ),
        rx.table.cell(
            rx.text(rx.fragment("€", item["price"]), weight="bold", size="2", color="#0F172A"),
            padding_y="0.6rem",
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(item["min_comp_name"], size="1", color="#94A3B8"),
                rx.text(item["min_comp_price_fmt"], weight="bold", size="2", color="#0F172A"),
                spacing="0", align_items="start",
            ),
            padding_y="0.6rem",
        ),
        rx.table.cell(pi_badge(item), padding_y="0.6rem"),
        rx.table.cell(
            rx.badge(
                rx.fragment("#", item["my_rank"]),
                color_scheme=item["color"],
                variant="surface", radius="full", size="1",
            ),
            padding_y="0.6rem",
        ),
        rx.table.cell(
            rx.text(item["nb_merchants"], size="2", color="#64748B"),
            padding_y="0.6rem",
        ),
        _hover={"bg": "#FAFAFA"},
        style=rx.cond(
            item["pi_color"] == "red",
            {"background": "#FFF5F5", "border_left": "2px solid #FCA5A5"},
            {},
        ),
    )


def brand_table():
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    col_header("PRODOTTO", "name"),
                    col_header("MIO PREZZO", "my_price"),
                    col_header("MIN COMP.", "min_price"),
                    col_header("PRICE INDEX", "price_index"),
                    col_header("RANK", "my_rank"),
                    col_header("N° COMP.", "nb_merchants"),
                    style={"bg": "#F8FAFC", "border_bottom": "1px solid #E2E8F0"},
                )
            ),
            rx.table.body(rx.foreach(State.filtered_product_list, product_row)),
            width="100%", variant="ghost",
        ),
        rx.hstack(
            rx.text(
                rx.fragment(State.page_number, " di ", State.total_pages,
                            " pagine — ", State.total_filtered, " prodotti"),
                size="1", color="#94A3B8",
            ),
            rx.spacer(),
            rx.hstack(
                rx.button(
                    rx.icon(tag="chevron-left", size=13), "Indietro",
                    on_click=State.prev_page, disabled=State.page_number == 1,
                    variant="ghost", color_scheme="gray", size="1",
                ),
                rx.button(
                    "Avanti", rx.icon(tag="chevron-right", size=13),
                    on_click=State.next_page,
                    disabled=State.page_number == State.total_pages,
                    variant="ghost", color_scheme="blue", size="1",
                ),
                spacing="1",
            ),
            width="100%", padding="0.75rem 1rem", align="center",
            border_top="1px solid #F1F5F9",
        ),
        width="100%", spacing="0",
    )


# ---------------------------------------------------------------------------
# PAGINA BRAND
# ---------------------------------------------------------------------------

def brand_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.button(
                        rx.hstack(rx.icon(tag="arrow-left", size=14),
                                  rx.text("Dashboard"), spacing="2", align="center"),
                        on_click=rx.redirect("/"),
                        variant="ghost", color_scheme="gray", size="2",
                    ),
                    rx.divider(orientation="vertical", height="24px", color="#E2E8F0"),
                    rx.vstack(
                        rx.heading(State.filter_brand, size="6", weight="bold", color="#0F172A"),
                        rx.text(
                            rx.fragment(State.total_filtered, " prodotti in catalogo"),
                            size="2", color="#64748B",
                        ),
                        spacing="0", align_items="start",
                    ),
                    width="100%", align="center", spacing="4",
                    bg="white", padding="1.25rem 1.5rem",
                    border_radius="12px", border="1px solid #E2E8F0",
                    box_shadow="0 1px 2px rgba(0,0,0,0.06)",
                ),

                # KPI brand
                rx.grid(
                    kpi_box("SKU Totali", State.total_filtered),
                    kpi_box("Price Index Medio", State.kpi_price_index_fmt,
                            color=rx.cond(State.kpi_pi_color == "red", "#DC2626",
                                          rx.cond(State.kpi_pi_color == "orange", "#D97706", "#16A34A"))),
                    kpi_box("Win Rate", State.kpi_win_rate, color="#16A34A"),
                    kpi_box("SKU Critici (PI>110)", State.kpi_critical_sku, color="#DC2626"),
                    columns=rx.breakpoints(initial="2", lg="4"),
                    spacing="3", width="100%",
                ),

                # Tabella prodotti del brand
                rx.box(
                    brand_table(),
                    bg="white", border_radius="12px",
                    box_shadow="0 1px 2px rgba(0,0,0,0.06)",
                    width="100%", border="1px solid #E2E8F0", overflow="auto",
                ),

                spacing="4", width="100%", align_items="stretch",
            ),
            width="100%", max_width="1400px",
            margin="0 auto", padding_x="2rem", padding_y="1.5rem",
        ),
        bg="#F1F5F9", min_height="100vh", width="100%",
    )