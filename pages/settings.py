import reflex as rx
from ..state import State
from ..components.navbar import navbar


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
        rx.text(
            text, size="2", weight="bold", color="#64748B",
            letter_spacing="0.06em", text_transform="uppercase",
        ),
        spacing="2", align="center", margin_bottom="1rem",
    )


def _competitor_slot_inner(index: int, label: str, current_val, on_change_handler):
    """Slot interno con handler esplicito."""
    return rx.vstack(
        rx.text(label, size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
        rx.hstack(
            rx.select.root(
                rx.select.trigger(placeholder="Nessuno", width="220px"),
                rx.select.content(
                    rx.select.item("— Nessuno —", value="__none__"),
                    rx.foreach(State.competitors, lambda c: rx.select.item(c, value=c)),
                    max_height="260px",
                ),
                value=current_val,
                on_change=on_change_handler,
            ),
            rx.cond(
                current_val != "",
                rx.icon(tag="circle-check", size=16, color="#22C55E"),
                rx.icon(tag="circle", size=16, color="#CBD5E1"),
            ),
            spacing="2", align="center",
        ),
        spacing="1", align_items="start",
    )


def competitor_slot(index: int, label: str):
    """Wrapper che seleziona il setter corretto per indice."""
    slots = [
        (State.preferred_competitors[0], State.set_pref_comp_0),
        (State.preferred_competitors[1], State.set_pref_comp_1),
        (State.preferred_competitors[2], State.set_pref_comp_2),
        (State.preferred_competitors[3], State.set_pref_comp_3),
        (State.preferred_competitors[4], State.set_pref_comp_4),
    ]
    current_val, handler = slots[index]
    return _competitor_slot_inner(index, label, current_val, handler)


def preferred_competitors_panel():
    return section_card(
        section_title("Competitor Preferiti", "users"),
        rx.text(
            "Scegli fino a 5 competitor da monitorare. Solo questi verranno mostrati nei confronti prezzi.",
            size="2", color="#64748B", margin_bottom="1.5rem",
        ),
        rx.grid(
            competitor_slot(0, "COMPETITOR #1"),
            competitor_slot(1, "COMPETITOR #2"),
            competitor_slot(2, "COMPETITOR #3"),
            competitor_slot(3, "COMPETITOR #4"),
            competitor_slot(4, "COMPETITOR #5"),
            columns=rx.breakpoints(initial="1", sm="2", lg="3"),
            spacing="4",
            width="100%",
        ),
        rx.divider(margin_y="1.25rem", color="#F1F5F9"),
        # Preview selezione attiva
        rx.vstack(
            rx.text("SELEZIONE ATTIVA", size="1", weight="bold", color="#94A3B8", letter_spacing="0.06em"),
            rx.flex(
                rx.foreach(
                    State.preferred_competitors,
                    lambda c: rx.cond(
                        c != "",
                        rx.hstack(
                            rx.icon(tag="circle-check", size=12, color="#22C55E"),
                            rx.text(c, size="2", weight="medium", color="#1E293B"),
                            spacing="1", align="center",
                            padding_x="0.75rem",
                            padding_y="0.3rem",
                            border_radius="999px",
                            bg="#F0FDF4",
                            border="1px solid #BBF7D0",
                        ),
                        rx.box(),
                    ),
                ),
                flex_wrap="wrap",
                gap="0.5rem",
            ),
            spacing="2", align_items="start",
        ),
    )


def competitor_box_panel():
    """Configura i 3 box KPI Aggressiveness nella home."""
    return section_card(
        section_title("Box KPI Dashboard", "layout-dashboard"),
        rx.text(
            "Scegli quali competitor mostrare nei box 'Aggressiveness' in cima alla dashboard.",
            size="2", color="#64748B", margin_bottom="1.5rem",
        ),
        rx.grid(
            rx.vstack(
                rx.text("BOX #1", size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
                rx.select.root(
                    rx.select.trigger(width="200px"),
                    rx.select.content(
                        rx.foreach(State.competitors, lambda c: rx.select.item(c, value=c)),
                        max_height="260px",
                    ),
                    value=State.comp_box_1,
                    on_change=State.set_comp_box_1,
                ),
                spacing="1", align_items="start",
            ),
            rx.vstack(
                rx.text("BOX #2", size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
                rx.select.root(
                    rx.select.trigger(width="200px"),
                    rx.select.content(
                        rx.foreach(State.competitors, lambda c: rx.select.item(c, value=c)),
                        max_height="260px",
                    ),
                    value=State.comp_box_2,
                    on_change=State.set_comp_box_2,
                ),
                spacing="1", align_items="start",
            ),
            rx.vstack(
                rx.text("BOX #3", size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
                rx.select.root(
                    rx.select.trigger(width="200px"),
                    rx.select.content(
                        rx.foreach(State.competitors, lambda c: rx.select.item(c, value=c)),
                        max_height="260px",
                    ),
                    value=State.comp_box_3,
                    on_change=State.set_comp_box_3,
                ),
                spacing="1", align_items="start",
            ),
            columns="3",
            spacing="4",
            width="100%",
        ),
    )


def sync_panel():
    """Pannello sincronizzazione dati."""
    return section_card(
        section_title("Sincronizzazione Dati", "refresh-cw"),
        rx.grid(
            rx.vstack(
                rx.text("STATO", size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
                rx.badge(State.sync_status, color_scheme="blue", variant="soft", radius="full"),
                spacing="1", align_items="start",
            ),
            rx.vstack(
                rx.text("AZIONE", size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
                rx.button(
                    rx.hstack(
                        rx.icon(tag="database", size=14),
                        rx.text("Genera Dati Demo"),
                        spacing="2", align="center",
                    ),
                    on_click=State.import_sensation_data,
                    loading=State.is_syncing,
                    color_scheme="blue",
                    variant="soft",
                    size="2",
                ),
                spacing="1", align_items="start",
            ),
            columns="2", spacing="4", width="100%",
        ),
    )


def ga4_panel():
    """Pannello configurazione GA4."""
    return section_card(
        section_title("Google Analytics 4", "bar-chart-2"),
        rx.grid(
            rx.vstack(
                rx.text("PROPERTY ID", size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
                rx.input(
                    placeholder="properties/123456789",
                    value=State.ga4_property_id,
                    on_change=State.set_ga4_property_id,
                    width="240px", size="2",
                ),
                spacing="1", align_items="start",
            ),
            rx.vstack(
                rx.text("STATO", size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
                rx.badge(State.ga4_status, color_scheme="green", variant="soft", radius="full"),
                rx.text(f"Ultimo sync: {State.last_sync_ga4}", size="1", color="#94A3B8"),
                spacing="1", align_items="start",
            ),
            rx.vstack(
                rx.text("AZIONI", size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
                rx.hstack(
                    rx.button(
                        "Salva Config",
                        on_click=State.save_ga4_config,
                        color_scheme="blue", variant="soft", size="2",
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon(tag="refresh-cw", size=13),
                            rx.text("Sync"),
                            spacing="1", align="center",
                        ),
                        on_click=State.sync_ga4_revenue,
                        loading=State.is_syncing_ga4,
                        color_scheme="green", variant="soft", size="2",
                    ),
                    spacing="2",
                ),
                spacing="1", align_items="start",
            ),
            columns=rx.breakpoints(initial="1", sm="3"),
            spacing="4", width="100%",
        ),
    )


def settings() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.vstack(
                # Intestazione
                rx.hstack(
                    rx.button(
                        rx.hstack(rx.icon(tag="arrow-left", size=14), rx.text("Dashboard"), spacing="2", align="center"),
                        on_click=rx.redirect("/"),
                        variant="ghost", color_scheme="gray", size="2",
                    ),
                    rx.divider(orientation="vertical", height="24px", color="#E2E8F0"),
                    rx.vstack(
                        rx.heading("Impostazioni", size="6", weight="bold", color="#0F172A"),
                        rx.text("Configura competitor, fonti dati e preferenze", size="2", color="#64748B"),
                        spacing="0", align_items="start",
                    ),
                    spacing="4", align="center", width="100%",
                    bg="white", padding="1.25rem 1.5rem",
                    border_radius="16px", border="1px solid #E2E8F0",
                    box_shadow="0 1px 3px rgba(0,0,0,0.06)",
                ),
                preferred_competitors_panel(),
                competitor_box_panel(),
                sync_panel(),
                ga4_panel(),
                spacing="4", width="100%", align_items="stretch",
            ),
            width="100%",
            max_width="1100px",
            margin="0 auto",
            padding_x="2rem",
            padding_y="1.5rem",
        ),
        bg="#F1F5F9",
        min_height="100vh",
        width="100%",
    )