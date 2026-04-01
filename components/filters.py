import reflex as rx
from ..state import State


def filter_label(text: str):
    return rx.text(text, size="1", weight="bold", color="#64748B", letter_spacing="0.06em")


def global_filter_bar():
    return rx.vstack(
        # --- RIGA 1: Date + Categoria + Cerca ---
        rx.flex(
            rx.hstack(
                rx.vstack(
                    filter_label("DAL:"),
                    rx.input(
                        type="date",
                        value=State.start_date,
                        on_change=State.set_start_date,
                        size="2",
                        width="140px",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                rx.vstack(
                    filter_label("AL:"),
                    rx.input(
                        type="date",
                        value=State.end_date,
                        on_change=State.set_end_date,
                        size="2",
                        width="140px",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                rx.divider(orientation="vertical", height="38px", color="#E2E8F0"),
                rx.vstack(
                    filter_label("CATEGORIA:"),
                    rx.select.root(
                        rx.select.trigger(width="160px"),
                        rx.select.content(
                            rx.foreach(
                                State.categories,
                                lambda c: rx.select.item(c, value=c),
                            ),
                            max_height="250px",
                        ),
                        value=State.filter_category,
                        on_change=State.set_filter_category,
                    ),
                    spacing="1",
                    align_items="start",
                ),
                rx.vstack(
                    filter_label("BRAND:"),
                    rx.select.root(
                        rx.select.trigger(width="160px"),
                        rx.select.content(
                            rx.foreach(
                                State.brands,
                                lambda b: rx.select.item(b, value=b),
                            ),
                            max_height="250px",
                        ),
                        value=State.filter_brand,
                        on_change=State.set_filter_brand,
                    ),
                    spacing="1",
                    align_items="start",
                ),
                rx.vstack(
                    filter_label("COMPETITOR:"),
                    rx.hstack(
                        rx.foreach(
                            State.preferred_competitors,
                            lambda c: rx.cond(
                                c != "",
                                rx.badge(
                                    c,
                                    color_scheme=rx.cond(
                                        State.filter_competitor.contains(c),
                                        "blue", "gray"
                                    ),
                                    variant=rx.cond(
                                        State.filter_competitor.contains(c),
                                        "solid", "outline"
                                    ),
                                    radius="full", size="2", cursor="pointer",
                                    on_click=State.set_filter_competitor(c),
                                ),
                                rx.box(),
                            ),
                        ),
                        spacing="2", flex_wrap="wrap",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                rx.vstack(
                    filter_label("CERCA:"),
                    rx.input(
                        placeholder="Nome prodotto o SKU...",
                        on_change=State.set_search_product,
                        width="200px",
                        size="2",
                        border_radius="8px",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                spacing="4",
                align="end",
                flex_wrap="wrap",
            ),
            width="100%",
        ),
        spacing="3",
        width="100%",
        bg="white",
        padding="1.25rem 1.5rem",
        border_radius="16px",
        box_shadow="0 1px 3px rgba(0,0,0,0.07)",
        border="1px solid #F1F5F9",
    )