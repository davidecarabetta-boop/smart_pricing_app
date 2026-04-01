import reflex as rx
from typing import Dict, Any
from ..state import State
from ..components.navbar import navbar
from ..components.filters import global_filter_bar


# ---------------------------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------------------------

def stat_card(label: str, value, sub: str = "", sub_color: str = "green"):
    return rx.vstack(
        rx.text(label, size="1", color="#94A3B8", weight="bold", letter_spacing="0.08em", text_transform="uppercase"),
        rx.heading(value, size="6", weight="bold", color="#0F172A"),
        rx.cond(
            sub != "",
            rx.badge(sub, color_scheme=sub_color, variant="soft", radius="full", size="1"),
            rx.box(),
        ),
        bg="white", padding="1rem 1.25rem", border_radius="12px",
        box_shadow="0 1px 2px rgba(0,0,0,0.06), 0 0 0 1px rgba(0,0,0,0.04)",
        width="100%", align_items="start", spacing="2", min_height="90px",
    )


def comp_card(name, value, trend, dot_color):
    is_active = State.filter_competitor.contains(name)
    return rx.cond(
        name != "",
        rx.hstack(
            rx.box(width="8px", height="8px", border_radius="50%", bg=dot_color, flex_shrink="0"),
            rx.vstack(
                rx.text(name, size="2", weight="bold", color=rx.cond(is_active, "#1D4ED8", "#334155"), no_of_lines=1),
                rx.text(value, size="4", weight="bold", color=rx.cond(is_active, "#1D4ED8", "#0F172A")),
                rx.text(trend, size="1", color="#94A3B8", no_of_lines=1),
                spacing="0", align_items="start",
            ),
            spacing="3", align="center", width="100%",
            padding="1rem", border_radius="10px",
            bg=rx.cond(is_active, "#EFF6FF", "#F8FAFC"),
            border=rx.cond(is_active, "1.5px solid #3B82F6", "1px solid #E2E8F0"),
            cursor="pointer",
            _hover={"border_color": "#3B82F6", "bg": "#F0F7FF"},
            on_click=State.select_competitor_filter(name),
        ),
        rx.box(
            rx.text("Non configurato", size="1", color="#CBD5E1"),
            padding="1rem", border_radius="10px",
            bg="#FAFAFA", border="1px dashed #E2E8F0",
            width="100%", text_align="center",
        ),
    )


def competitors_widget():
    return rx.vstack(
        rx.hstack(
            rx.icon(tag="activity", size=14, color="#94A3B8"),
            rx.text("COMPETITOR AGGRESSIVENESS", size="1", weight="bold", color="#94A3B8", letter_spacing="0.08em"),
            rx.spacer(),
            rx.cond(
                State.filter_competitor.length() > 0,
                rx.button(
                    "Reset filtro", size="1", variant="ghost", color_scheme="gray",
                    on_click=State.set_filter_competitor("Tutti"),
                ),
                rx.text("Clicca per filtrare", size="1", color="#CBD5E1"),
            ),
            spacing="2", align="center", width="100%",
        ),
        rx.grid(
            comp_card(State.preferred_competitors[0], State.comp_aggr_1, State.comp_label_1, "#EF4444"),
            comp_card(State.preferred_competitors[1], State.comp_aggr_2, State.comp_label_2, "#3B82F6"),
            comp_card(State.preferred_competitors[2], State.comp_aggr_3, State.comp_label_3, "#8B5CF6"),
            comp_card(State.preferred_competitors[3], State.comp_aggr_4, State.comp_label_4, "#F59E0B"),
            comp_card(State.preferred_competitors[4], State.comp_aggr_5, State.comp_label_5, "#10B981"),
            columns="5", spacing="3", width="100%",
        ),
        bg="white", padding="1.25rem 1.5rem", border_radius="12px",
        box_shadow="0 1px 2px rgba(0,0,0,0.06), 0 0 0 1px rgba(0,0,0,0.04)",
        width="100%", align_items="start", spacing="3",
    )


def critical_banner():
    return rx.hstack(
        rx.box(
            rx.icon(tag="triangle-alert", size=18, color="white"),
            bg="#EF4444", padding="0.5rem", border_radius="8px", flex_shrink="0",
        ),
        rx.vstack(
            rx.text("SKU CRITICI", size="1", weight="bold", color="#7F1D1D", letter_spacing="0.08em"),
            rx.hstack(
                rx.heading(State.kpi_critical_sku, size="6", weight="bold", color="#0F172A"),
                rx.text("Price Index > 110", size="2", color="#64748B", margin_top="4px"),
                spacing="2", align="end",
            ),
            spacing="0", align_items="start",
        ),
        spacing="3", align="center",
        bg="white", padding="1rem 1.25rem", border_radius="12px",
        box_shadow="0 1px 2px rgba(0,0,0,0.06), 0 0 0 1px rgba(0,0,0,0.04)",
        width="100%", min_height="90px",
        border_left="3px solid #EF4444",
    )


# ---------------------------------------------------------------------------
# TABELLA
# ---------------------------------------------------------------------------

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


def pi_cell(item: dict):
    """Price Index con barra colorata."""
    return rx.vstack(
        rx.hstack(
            rx.text(
                item["price_index_fmt"],
                weight="bold", size="2",
                color=rx.cond(
                    item["pi_color"] == "red", "#DC2626",
                    rx.cond(item["pi_color"] == "orange", "#D97706", "#16A34A")
                ),
            ),
            spacing="1", align="center",
        ),
        rx.box(
            rx.box(
                height="3px",
                width=rx.cond(
                    item["pi_color"] == "red", "100%",
                    rx.cond(item["pi_color"] == "orange", "60%", "30%")
                ),
                bg=rx.cond(
                    item["pi_color"] == "red", "#EF4444",
                    rx.cond(item["pi_color"] == "orange", "#F59E0B", "#22C55E")
                ),
                border_radius="2px",
            ),
            width="60px", height="3px", bg="#F1F5F9", border_radius="2px",
        ),
        spacing="1", align_items="start",
    )


def product_row(item: dict):
    return rx.table.row(
        # Prodotto
        rx.table.cell(
            rx.vstack(
                rx.text(
                    item["name"], weight="medium", color="#1E40AF", cursor="pointer", size="2",
                    _hover={"text_decoration": "underline"},
                    on_click=State.nav_to_product_detail(item["sku"]),
                ),
                rx.hstack(
                    rx.badge(item["brand"], variant="outline", size="1", color_scheme="gray"),
                    rx.badge(item["category"], variant="soft", size="1", color_scheme="blue"),
                    spacing="1",
                ),
                spacing="1", align_items="start",
            ),
            padding_y="0.6rem", min_width="200px",
        ),
        # Brand
        rx.table.cell(
            rx.text(
                item["brand"], size="2", color="#1E40AF", weight="medium",
                cursor="pointer",
                _hover={"text_decoration": "underline"},
                on_click=State.nav_to_brand(item["brand"]),
            ),
            padding_y="0.6rem",
        ),
        # Trend
        rx.table.cell(
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="val",
                    stroke=rx.cond(
                        item["color"] == "green", "#22C55E",
                        rx.cond(item["color"] == "orange", "#F59E0B", "#EF4444")
                    ),
                    dot=False, stroke_width=2,
                ),
                data=[{"val": 10}, {"val": 8}, {"val": 9}, {"val": 7}, {"val": 8}, {"val": 9}, {"val": 11}, {"val": 10}],
                width=80, height=30,
            ),
            padding_y="0.6rem",
        ),
        # Mio prezzo
        rx.table.cell(
            rx.text(rx.fragment("€", item["price"]), weight="bold", size="2", color="#0F172A"),
            padding_y="0.6rem",
        ),
        # Min competitor
        rx.table.cell(
            rx.vstack(
                rx.text(item["min_comp_name"], size="1", color="#94A3B8"),
                rx.text(item["min_comp_price_fmt"], weight="bold", size="2", color="#0F172A"),
                spacing="0", align_items="start",
            ),
            padding_y="0.6rem",
        ),
        # Price Index
        rx.table.cell(pi_cell(item), padding_y="0.6rem"),
        # Rank
        rx.table.cell(
            rx.badge(
                rx.fragment("#", item["my_rank"]),
                color_scheme=item["color"],
                variant="surface", radius="full", size="1",
            ),
            padding_y="0.6rem",
        ),
        # N° Merchant
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


def product_table():
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    col_header("PRODOTTO", "name"),
                    col_header("BRAND", "brand"),
                    rx.table.column_header_cell(rx.text("TREND", size="1", weight="bold", color="#64748B", letter_spacing="0.05em")),
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
        # Paginazione
        rx.hstack(
            rx.text(
                rx.fragment(State.page_number, " di ", State.total_pages, " pagine — ", State.total_filtered, " prodotti"),
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
                    on_click=State.next_page, disabled=State.page_number == State.total_pages,
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
# GRAFICO
# ---------------------------------------------------------------------------

def price_index_chart():
    return rx.vstack(
        rx.hstack(
            rx.icon(tag="trending-up", size=14, color="#94A3B8"),
            rx.text("ANDAMENTO PRICE INDEX — ultimi 30 giorni", size="1", weight="bold", color="#94A3B8", letter_spacing="0.06em"),
            spacing="2", align="center",
        ),
        rx.recharts.area_chart(
            rx.recharts.area(
                data_key="price_index",
                stroke="#3B82F6", fill="#DBEAFE",
                stroke_width=2, dot=False, name="Price Index",
            ),
            rx.recharts.x_axis(
                data_key="name",
                tick={"fill": "#94A3B8", "fontSize": 11},
                axis_line=False, tick_line=False,
            ),
            rx.recharts.y_axis(
                tick={"fill": "#94A3B8", "fontSize": 11},
                axis_line=False, tick_line=False,
            ),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke="#F1F5F9", vertical=False),
            rx.recharts.graphing_tooltip(),
            rx.recharts.reference_line(y=100, stroke="#22C55E", stroke_dasharray="4 4", label="100"),
            data=State.chart_data,
            width="100%", height=200,
        ),
        bg="white", padding="1.25rem 1.5rem", border_radius="12px",
        box_shadow="0 1px 2px rgba(0,0,0,0.06)", border="1px solid #F1F5F9",
        width="100%", align_items="start", spacing="3",
    )


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------

def home() -> rx.Component:
    return rx.box(
        navbar(),
        rx.vstack(
            # --- KPI ROW ---
            rx.grid(
                stat_card(
                    "POSIZIONAMENTO",
                    rx.hstack(
                        rx.text(State.win_rate_count, size="6", weight="bold", color="#0F172A"),
                        rx.text("SKU #1", size="2", color="#64748B"),
                        spacing="2", align="end",
                    ),
                    f"Win rate {State.win_rate}",
                    "green",
                ),
                stat_card(
                    "PRICE INDEX MEDIO",
                    State.kpi_price_index_fmt,
                    State.pi_pts,
                    State.pi_color,
                ),
                critical_banner(),
                columns=rx.breakpoints(initial="1", sm="3"),
                spacing="3", width="100%",
            ),

            # --- COMPETITOR WIDGET (riga intera) ---
            competitors_widget(),

            # --- FILTRI ---
            global_filter_bar(),

            # --- GRAFICO ---
            price_index_chart(),

            # --- HEADER TABELLA ---
            rx.hstack(
                rx.heading(
                    rx.cond(State.filter_category == "Tutte", "Tutti i Prodotti", State.filter_category),
                    size="3", weight="bold", color="#0F172A",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.badge(
                        rx.hstack(
                            rx.icon(tag="database", size=11),
                            rx.text(rx.fragment(State.total_products, " prodotti")),
                            spacing="1", align="center",
                        ),
                        color_scheme="blue", variant="soft", radius="full", size="1",
                    ),
                    rx.cond(
                        State.filter_competitor.length() > 0,
                        rx.badge(
                            rx.hstack(
                                rx.icon(tag="filter", size=11),
                                rx.text(rx.fragment(State.filter_competitor.length(), " competitor attivi")),
                                rx.icon(
                                    tag="x", size=10, cursor="pointer",
                                    on_click=State.set_filter_competitor("Tutti"),
                                ),
                                spacing="1", align="center",
                            ),
                            color_scheme="blue", variant="surface", radius="full",
                            size="1", cursor="pointer",
                        ),
                        rx.box(),
                    ),
                    spacing="2",
                ),
                width="100%", align="center",
            ),

            # --- TABELLA ---
            rx.box(
                product_table(),
                bg="white", border_radius="12px",
                box_shadow="0 1px 2px rgba(0,0,0,0.06)",
                width="100%", border="1px solid #E2E8F0", overflow="auto",
            ),

            spacing="4", width="100%",
            padding_x="2rem", padding_y="1.5rem",
            max_width="1600px", margin="0 auto",
        ),
        bg="#F1F5F9", min_height="100vh", width="100%",
    )