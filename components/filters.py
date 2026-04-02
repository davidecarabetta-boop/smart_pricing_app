import reflex as rx
from ..state import State


# =============================================================================
# COMPONENTI INTERNI
# =============================================================================

def _filter_label(text: str) -> rx.Component:
    """Label piccola sopra il filtro."""
    return rx.text(
        text, size="1", weight="bold", color="#94A3B8",
        letter_spacing="0.06em", text_transform="uppercase",
    )


def _preset_pill(label: str, days: int) -> rx.Component:
    """
    Pill per preset rapido.
    Confronta con start_date per capire se è attiva.
    days=0 → Oggi, days=7 → 7gg, ecc.
    """
    return rx.button(
        label,
        size="1",
        variant="solid" if _is_preset_active(days) else "outline",
        color_scheme="blue" if _is_preset_active(days) else "gray",
        border_radius="999px",
        on_click=State.set_date_preset(days),
        cursor="pointer",
        _hover={"opacity": "0.85"},
    )


def _is_preset_active(days: int):
    """
    Verifica se il preset corrisponde al range attuale.
    Non possiamo fare logica Python pura qui (è Reflex),
    quindi usiamo una versione semplificata.
    """
    # In Reflex non possiamo fare calcoli dinamici nelle props statiche,
    # ma i bottoni funzionano comunque — il colore attivo lo gestiamo via State
    # Per ora tutti i pill partono come "outline" e il click setta le date
    return False


# =============================================================================
# SEZIONE DATE
# =============================================================================

def date_filter_section() -> rx.Component:
    """Blocco filtro date: preset + date picker + label range."""
    return rx.vstack(
        # Riga 1: Preset pill rapide
        rx.hstack(
            rx.icon(tag="calendar-range", size=14, color="#1D4ED8"),
            rx.button(
                "Oggi", size="1", variant="outline", color_scheme="blue",
                border_radius="999px", on_click=State.set_date_preset(0),
            ),
            rx.button(
                "7gg", size="1", variant="outline", color_scheme="blue",
                border_radius="999px", on_click=State.set_date_preset(7),
            ),
            rx.button(
                "30gg", size="1", variant="solid", color_scheme="blue",
                border_radius="999px", on_click=State.set_date_preset(30),
            ),
            rx.button(
                "90gg", size="1", variant="outline", color_scheme="blue",
                border_radius="999px", on_click=State.set_date_preset(90),
            ),
            rx.button(
                "1 anno", size="1", variant="outline", color_scheme="blue",
                border_radius="999px", on_click=State.set_date_preset(365),
            ),
            spacing="2",
            align="center",
            flex_wrap="wrap",
        ),

        # Riga 2: Date picker Da → A
        rx.hstack(
            _filter_label("Da"),
            rx.input(
                type="date",
                value=State.start_date,
                on_change=State.set_start_date,
                size="1",
                width="145px",
                border_radius="8px",
                border="1px solid #CBD5E1",
                _focus={"border": "1px solid #1D4ED8", "box_shadow": "0 0 0 2px rgba(29,78,216,0.15)"},
            ),
            rx.icon(tag="arrow-right", size=14, color="#94A3B8"),
            _filter_label("A"),
            rx.input(
                type="date",
                value=State.end_date,
                on_change=State.set_end_date,
                size="1",
                width="145px",
                border_radius="8px",
                border="1px solid #CBD5E1",
                _focus={"border": "1px solid #1D4ED8", "box_shadow": "0 0 0 2px rgba(29,78,216,0.15)"},
            ),
            spacing="2",
            align="center",
        ),

        # Riga 3: Label range attivo + confronto periodo precedente
        rx.hstack(
            rx.hstack(
                rx.icon(tag="info", size=12, color="#64748B"),
                rx.text(
                    State.date_range_label,
                    size="1", color="#64748B", font_style="italic",
                ),
                spacing="1", align="center",
            ),
            rx.spacer(),
            # Toggle confronto periodo precedente
            rx.hstack(
                rx.switch(
                    checked=State.compare_mode,
                    on_change=State.set_compare_mode,
                    size="1",
                    color_scheme="blue",
                ),
                rx.text(
                    "Confronta",
                    size="1", color="#64748B", weight="medium",
                ),
                spacing="1", align="center",
            ),
            width="100%",
            align="center",
        ),

        # Riga 4: Label periodo precedente (visibile solo se compare_mode)
        rx.cond(
            State.compare_mode,
            rx.hstack(
                rx.icon(tag="git-compare-arrows", size=12, color="#8B5CF6"),
                rx.text(
                    State.previous_period_label,
                    size="1", color="#8B5CF6", weight="medium",
                ),
                spacing="1", align="center",
            ),
            rx.fragment(),
        ),

        spacing="3",
        align_items="start",
    )


# =============================================================================
# SEZIONE FILTRI CLASSICI (brand, categoria, cerca)
# =============================================================================

def classic_filters_section() -> rx.Component:
    """Filtri brand, categoria, ricerca."""
    return rx.hstack(
        # Brand
        rx.vstack(
            _filter_label("Brand"),
            rx.select.root(
                rx.select.trigger(placeholder="Tutti", min_width="140px"),
                rx.select.content(
                    rx.foreach(
                        State.brands,
                        lambda b: rx.select.item(b, value=b),
                    ),
                    max_height="260px",
                ),
                value=State.filter_brand,
                on_change=State.set_filter_brand,
            ),
            spacing="1", align_items="start",
        ),

        # Categoria
        rx.vstack(
            _filter_label("Categoria"),
            rx.select.root(
                rx.select.trigger(placeholder="Tutte", min_width="160px"),
                rx.select.content(
                    rx.foreach(
                        State.categories,
                        lambda c: rx.select.item(c, value=c),
                    ),
                    max_height="260px",
                ),
                value=State.filter_category,
                on_change=State.set_filter_category,
            ),
            spacing="1", align_items="start",
        ),

        # Ricerca
        rx.vstack(
            _filter_label("Cerca"),
            rx.input(
                rx.input.slot(rx.icon(tag="search", size=14, color="#94A3B8")),
                placeholder="Nome o SKU...",
                value=State.search_product,
                on_change=State.set_search_product,
                size="2",
                width="220px",
                border_radius="8px",
                border="1px solid #CBD5E1",
                _focus={"border": "1px solid #1D4ED8", "box_shadow": "0 0 0 2px rgba(29,78,216,0.15)"},
            ),
            spacing="1", align_items="start",
        ),

        spacing="4",
        align="end",
        flex_wrap="wrap",
    )


# =============================================================================
# BARRA FILTRI GLOBALE — ESPORTATA
# =============================================================================

def global_filter_bar() -> rx.Component:
    """
    Barra filtri completa: filtri classici + date.
    Layout: due blocchi affiancati su desktop, impilati su mobile.
    """
    return rx.box(
        rx.flex(
            # Lato sinistro: Brand, Categoria, Cerca
            classic_filters_section(),

            # Separatore verticale (solo desktop)
            rx.divider(
                orientation="vertical",
                height="80px",
                color="#E2E8F0",
                display=rx.breakpoints(initial="none", lg="block"),
            ),

            # Lato destro: Date
            date_filter_section(),

            spacing="5",
            width="100%",
            align="start",
            flex_wrap="wrap",
            justify="between",
        ),
        bg="white",
        padding="1.25rem 1.5rem",
        border_radius="16px",
        border="1px solid #E2E8F0",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
        width="100%",
    )