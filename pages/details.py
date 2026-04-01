import reflex as rx
from ..state import State
from ..components.navbar import navbar


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def section_card(*children, **props):
    return rx.box(
        *children,
        bg="white",
        border_radius="16px",
        padding="1.5rem",
        border="1px solid #E2E8F0",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
        width="100%",
        **props,
    )


def section_title(text: str, icon: str):
    return rx.hstack(
        rx.icon(tag=icon, size=16, color="#64748B"),
        rx.text(text, size="2", weight="bold", color="#64748B", letter_spacing="0.06em", text_transform="uppercase"),
        spacing="2",
        align="center",
        margin_bottom="1rem",
    )


def kpi_box(label: str, value, color: str = "#0F172A", bg: str = "#F8FAFC"):
    return rx.vstack(
        rx.text(label, size="1", weight="bold", color="#94A3B8", letter_spacing="0.06em", text_transform="uppercase"),
        rx.heading(value, size="6", weight="bold", color=color),
        padding="1rem 1.25rem",
        bg=bg,
        border_radius="12px",
        border="1px solid #E2E8F0",
        align_items="start",
        spacing="1",
        width="100%",
    )


# ---------------------------------------------------------------------------
# SEZIONE 1 — INTESTAZIONE PRODOTTO
# ---------------------------------------------------------------------------

def product_header():
    return rx.hstack(
        rx.button(
            rx.hstack(rx.icon(tag="arrow-left", size=14), rx.text("Dashboard"), spacing="2", align="center"),
            on_click=rx.redirect("/"),
            variant="ghost", color_scheme="gray", size="2",
        ),
        rx.divider(orientation="vertical", height="24px", color="#E2E8F0"),
        rx.vstack(
            rx.heading(State.selected_product_name, size="6", weight="bold", color="#0F172A"),
            rx.hstack(
                rx.badge(State.selected_product_brand, variant="outline", size="1", color_scheme="gray"),
                rx.badge(State.selected_product_category, variant="soft", size="1", color_scheme="blue"),
                rx.badge(State.selected_product_sku, variant="soft", size="1", color_scheme="gray"),
                spacing="2",
            ),
            spacing="1", align_items="start",
        ),
        rx.spacer(),
        rx.vstack(
            rx.heading(rx.fragment("€ ", State.selected_product_price), size="7", weight="bold", color="#0F172A"),
            rx.badge(
                rx.hstack(
                    rx.icon(tag="trophy", size=11),
                    rx.text(rx.fragment("Posizione: ", State.selected_product_pos)),
                    spacing="1", align="center",
                ),
                color_scheme=State.selected_product_pos_color,
                variant="surface", radius="full",
            ),
            align_items="end", spacing="1",
        ),
        width="100%", align="center", spacing="4",
        bg="white", padding="1.25rem 1.5rem",
        border_radius="16px", border="1px solid #E2E8F0",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
    )


# ---------------------------------------------------------------------------
# SEZIONE 2 — KPI PRODOTTO
# ---------------------------------------------------------------------------

def kpi_row():
    return rx.grid(
        kpi_box("Revenue (30gg)", rx.fragment("€ ", State.selected_product_revenue), "#0F172A"),
        kpi_box("Unità Vendute", State.selected_product_units, "#0F172A"),
        kpi_box("Price Index vs #1", State.selected_price_index_label,
                color=State.selected_price_index_color),
        kpi_box("Prezzo Suggerito", rx.fragment("€ ", State.suggested_price), "#059669", "#F0FDF4"),
        columns=rx.breakpoints(initial="2", lg="4"),
        spacing="3", width="100%",
    )


# ---------------------------------------------------------------------------
# SEZIONE 3 — TOP 3 COMPETITOR
# ---------------------------------------------------------------------------

def competitor_delta_badge(delta: str, color: str):
    return rx.badge(delta, color_scheme=color, variant="soft", radius="full", size="1")


def competitor_row(comp: dict):
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                rx.box(width="8px", height="8px", border_radius="50%", bg=comp["dot_color"]),
                rx.text(comp["name"], weight="medium", size="2"),
                spacing="2", align="center",
            ),
            padding_y="0.75rem",
        ),
        rx.table.cell(
            rx.text(rx.fragment("€ ", comp["price"]), weight="bold", size="2"),
            padding_y="0.75rem",
        ),
        rx.table.cell(
            rx.badge(
                comp["delta"],
                color_scheme=comp["delta_color"],
                variant="soft", radius="full", size="1",
            ),
            padding_y="0.75rem",
        ),
        rx.table.cell(
            rx.badge(
                comp["availability"],
                color_scheme=rx.cond(comp["availability"] == "Disponibile", "green", "gray"),
                variant="soft", radius="full", size="1",
            ),
            padding_y="0.75rem",
        ),
        _hover={"bg": "#F8FAFC"},
    )


def competitor_table():
    return section_card(
        section_title("Top Competitor", "users"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        rx.text("COMPETITOR", size="1", weight="bold", color="#64748B", letter_spacing="0.06em")
                    ),
                    rx.table.column_header_cell(
                        rx.text("PREZZO", size="1", weight="bold", color="#64748B", letter_spacing="0.06em")
                    ),
                    rx.table.column_header_cell(
                        rx.text("DELTA vs TUO", size="1", weight="bold", color="#64748B", letter_spacing="0.06em")
                    ),
                    rx.table.column_header_cell(
                        rx.text("DISPONIBILITÀ", size="1", weight="bold", color="#64748B", letter_spacing="0.06em")
                    ),
                    style={"bg": "#F8FAFC", "border_bottom": "2px solid #E2E8F0"},
                )
            ),
            rx.table.body(
                rx.foreach(State.selected_competitors, competitor_row)
            ),
            width="100%", variant="ghost",
        ),
    )


# ---------------------------------------------------------------------------
# SEZIONE 4 — GRAFICO STORICO PREZZI
# ---------------------------------------------------------------------------

def price_history_chart():
    return section_card(
        section_title("Storico Prezzi (30gg)", "trending-up"),
        rx.recharts.line_chart(
            rx.recharts.line(
                data_key="price",
                stroke="#3B82F6",
                stroke_width=2,
                dot=False,
                name="Tuo Prezzo",
            ),
            rx.recharts.line(
                data_key="market",
                stroke="#CBD5E1",
                stroke_width=2,
                dot=False,
                stroke_dasharray="4 4",
                name="Miglior Competitor",
            ),
            rx.recharts.x_axis(
                data_key="name",
                tick={"fill": "#94A3B8", "fontSize": 11},
                axisLine=False, tickLine=False,
            ),
            rx.recharts.y_axis(
                tick={"fill": "#94A3B8", "fontSize": 11},
                axisLine=False, tickLine=False,
            ),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke="#F1F5F9", vertical=False),
            rx.recharts.legend(),
            rx.recharts.graphing_tooltip(
                content_style={
                    "background": "white",
                    "border": "1px solid #E2E8F0",
                    "borderRadius": "8px",
                    "boxShadow": "0 4px 6px rgba(0,0,0,0.07)",
                },
            ),
            data=State.chart_data,
            width="100%", height=260,
        ),
    )


# ---------------------------------------------------------------------------
# SEZIONE 5 — STORICO POSIZIONAMENTO
# ---------------------------------------------------------------------------

def positioning_history():
    return section_card(
        section_title("Storico Posizionamento", "bar-chart-2"),
        rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="score",
                fill="#3B82F6",
                radius=[4, 4, 0, 0],
                name="Posizione",
            ),
            rx.recharts.x_axis(
                data_key="name",
                tick={"fill": "#94A3B8", "fontSize": 11},
                axis_line=False, tick_line=False,
            ),
            rx.recharts.y_axis(
                domain=[0, 5],
                tick={"fill": "#94A3B8", "fontSize": 11},
                axis_line=False, tick_line=False,
                ticks=[1, 2, 3, 4, 5],
            ),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke="#F1F5F9", vertical=False),
            rx.recharts.graphing_tooltip(),
            data=State.positioning_history,
            width="100%", height=200,
        ),
        rx.text(
            "Barre alte = buon posizionamento (#1), barre basse = posizione lontana",
            size="1", color="#94A3B8", margin_top="0.5rem",
        ),
    )


# ---------------------------------------------------------------------------
# SEZIONE 6 — REGOLE REPRICING
# ---------------------------------------------------------------------------

def repricing_rule_row(rule: dict):
    return rx.hstack(
        rx.icon(tag="zap", size=14, color="#F59E0B"),
        rx.text(rule["label"], size="2", color="#334155"),
        rx.spacer(),
        rx.badge(rule["status"], color_scheme=rule["status_color"], variant="soft", radius="full", size="1"),
        rx.button(
            rx.icon(tag="pencil", size=12),
            size="1", variant="ghost", color_scheme="gray",
        ),
        width="100%", align="center", spacing="3",
        padding="0.6rem 0.75rem",
        border_radius="8px",
        bg="#FFFBEB",
        border="1px solid #FDE68A",
    )


def repricing_panel():
    return section_card(
        section_title("Regole Repricing", "zap"),
        rx.vstack(
            rx.foreach(State.selected_repricing_rules, repricing_rule_row),
            rx.button(
                rx.hstack(
                    rx.icon(tag="plus", size=14),
                    rx.text("Aggiungi Regola"),
                    spacing="2", align="center",
                ),
                variant="outline", color_scheme="amber",
                width="100%", size="2",
            ),
            spacing="2", width="100%",
        ),
    )


# ---------------------------------------------------------------------------
# LAYOUT PRINCIPALE
# ---------------------------------------------------------------------------

def details() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.vstack(
                product_header(),
                kpi_row(),
                # Riga: competitor + repricing affiancati
                rx.grid(
                    competitor_table(),
                    repricing_panel(),
                    columns=rx.breakpoints(initial="1", lg="2"),
                    spacing="4", width="100%",
                ),
                # Riga: grafici affiancati
                rx.grid(
                    price_history_chart(),
                    positioning_history(),
                    columns=rx.breakpoints(initial="1", lg="2"),
                    spacing="4", width="100%",
                ),
                spacing="4", width="100%", align_items="stretch",
            ),
            width="100%",
            max_width="1400px",
            margin="0 auto",
            padding_x="2rem",
            padding_y="1.5rem",
        ),
        bg="#F1F5F9",
        min_height="100vh",
        width="100%",
    )