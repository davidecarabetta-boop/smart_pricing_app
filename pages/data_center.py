import reflex as rx
from ..state import State
from ..components.navbar import navbar


def section_card(*children, **props):
    return rx.box(
        *children,
        bg="white", border_radius="12px", padding="1.25rem 1.5rem",
        border="1px solid #E2E8F0",
        box_shadow="0 1px 2px rgba(0,0,0,0.06)",
        width="100%", **props,
    )


def section_title(text: str, icon: str):
    return rx.hstack(
        rx.icon(tag=icon, size=16, color="#64748B"),
        rx.text(text, size="2", weight="bold", color="#64748B",
                letter_spacing="0.06em", text_transform="uppercase"),
        spacing="2", align="center", margin_bottom="1rem",
    )


def ga4_panel():
    return section_card(
        section_title("Google Analytics 4", "bar-chart-2"),
        rx.grid(
            # Property ID
            rx.vstack(
                rx.text("PROPERTY ID", size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
                rx.input(
                    placeholder="es. 123456789",
                    value=State.ga4_property_id,
                    on_change=State.set_ga4_property_id,
                    width="100%", size="2",
                ),
                rx.text("Trovalo in GA4 → Admin → Property Settings", size="1", color="#94A3B8"),
                spacing="1", align_items="start", width="100%",
            ),
            # Stato connessione
            rx.vstack(
                rx.text("STATO", size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
                rx.badge(
                    State.ga4_status,
                    color_scheme=rx.cond(
                        State.ga4_status == "Connesso ✅", "green",
                        rx.cond(State.ga4_status == "Non configurato", "gray", "red")
                    ),
                    variant="soft", radius="full",
                ),
                rx.text(rx.fragment("Ultimo sync: ", State.last_sync_ga4), size="1", color="#94A3B8"),
                spacing="1", align_items="start",
            ),
            columns=rx.breakpoints(initial="1", sm="2"),
            spacing="4", width="100%", margin_bottom="1.5rem",
        ),

        # Upload JSON
        rx.vstack(
            rx.text("SERVICE ACCOUNT JSON", size="1", weight="bold", color="#64748B", letter_spacing="0.05em"),
            rx.upload(
                rx.vstack(
                    rx.icon(tag="upload", size=24, color="#94A3B8"),
                    rx.text("Trascina il file JSON qui", size="2", color="#64748B"),
                    rx.text("o clicca per selezionarlo", size="1", color="#94A3B8"),
                    spacing="1", align="center",
                ),
                id="ga4_json_upload",
                accept={".json": "application/json"},
                border="2px dashed #E2E8F0",
                border_radius="10px",
                padding="2rem",
                width="100%",
                _hover={"border_color": "#3B82F6", "bg": "#F0F7FF"},
                cursor="pointer",
            ),
            rx.cond(
                rx.selected_files("ga4_json_upload").length() > 0,
                rx.hstack(
                    rx.icon(tag="file-check", size=14, color="#16A34A"),
                    rx.text(
                        rx.selected_files("ga4_json_upload")[0],
                        size="2", color="#16A34A", weight="medium",
                    ),
                    spacing="2", align="center",
                ),
                rx.box(),
            ),
            spacing="2", width="100%",
        ),

        rx.divider(margin_y="1.25rem"),

        # Azioni
        rx.hstack(
            rx.button(
                rx.hstack(
                    rx.icon(tag="plug", size=14),
                    rx.text("Connetti GA4"),
                    spacing="2", align="center",
                ),
                on_click=State.connect_ga4(rx.upload_files(upload_id="ga4_json_upload")),
                color_scheme="blue", variant="solid", size="2",
            ),
            rx.button(
                rx.hstack(
                    rx.icon(tag="refresh-cw", size=14),
                    rx.text("Sync Revenue"),
                    spacing="2", align="center",
                ),
                on_click=State.sync_ga4_revenue,
                loading=State.is_syncing_ga4,
                color_scheme="green", variant="soft", size="2",
                disabled=State.ga4_status != "Connesso ✅",
            ),
            spacing="3",
        ),
    )


def sync_panel():
    return section_card(
        section_title("Sincronizzazione AlphaPosition", "refresh-cw"),
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
                        rx.icon(tag="refresh-cw", size=14),
                        rx.text("Sincronizza Ora"),
                        spacing="2", align="center",
                    ),
                    on_click=State.sync_prices,
                    loading=State.is_syncing,
                    color_scheme="green", variant="soft", size="2",
                ),
                spacing="1", align_items="start",
            ),
            columns="2", spacing="4", width="100%",
        ),
        rx.cond(
            State.is_syncing,
            rx.vstack(
                rx.text(State.sync_current_product, size="1", color="#94A3B8"),
                rx.progress(value=State.sync_progress, max=100, width="100%"),
                spacing="1", margin_top="1rem", width="100%",
            ),
            rx.box(),
        ),
    )


def data_center() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.button(
                        rx.hstack(rx.icon(tag="arrow-left", size=14), rx.text("Dashboard"),
                                  spacing="2", align="center"),
                        on_click=rx.redirect("/"),
                        variant="ghost", color_scheme="gray", size="2",
                    ),
                    rx.divider(orientation="vertical", height="24px", color="#E2E8F0"),
                    rx.vstack(
                        rx.heading("Data Center", size="6", weight="bold", color="#0F172A"),
                        rx.text("Gestisci sorgenti dati e integrazioni", size="2", color="#64748B"),
                        spacing="0", align_items="start",
                    ),
                    spacing="4", align="center", width="100%",
                    bg="white", padding="1.25rem 1.5rem",
                    border_radius="12px", border="1px solid #E2E8F0",
                    box_shadow="0 1px 2px rgba(0,0,0,0.06)",
                ),

                ga4_panel(),
                sync_panel(),

                spacing="4", width="100%", align_items="stretch",
            ),
            width="100%", max_width="900px",
            margin="0 auto", padding_x="2rem", padding_y="1.5rem",
        ),
        bg="#F1F5F9", min_height="100vh", width="100%",
    )