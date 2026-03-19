import reflex as rx
from ..components.navbar import navbar


def strategy_card(title: str, description: str, icon: str, color: str) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(rx.icon(icon, size=16), color_scheme=color, variant="soft", radius="full", padding="0.5rem"),
                rx.spacer(),
                rx.switch(default_checked=False, color_scheme=color),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.heading(title, size="4", weight="bold"),
                rx.text(description, size="2", color="gray"),
                spacing="1",
                align_items="start",
            ),
            rx.divider(),
            rx.hstack(
                rx.text("Delta %", size="2", weight="medium"),
                rx.input(placeholder="-1.0%", size="1", width="70px"),
                rx.spacer(),
                rx.text("Priorità", size="2"),
                rx.badge("Alta", color_scheme="orange"),
                width="100%",
                align="center",
            ),
            spacing="4",
            padding="1rem",
        ),
        width="100%",
        style={"&:hover": {"box_shadow": "0 4px 12px rgba(0,0,0,0.1)"}},
    )


def strategie() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.container(
            rx.vstack(
                rx.vstack(
                    rx.heading("Strategie di Repricing", size="8", weight="bold"),
                    rx.text("Definisci le regole che Gemini userà per calcolare i tuoi prezzi target.", color="gray"),
                    align_items="start",
                    spacing="1",
                ),

                # Griglia delle strategie
                rx.grid(
                    strategy_card(
                        "Price Matcher",
                        "Aggancia il prezzo al competitor più economico (es. Notino).",
                        "target", "blue"
                    ),
                    strategy_card(
                        "Margin Protector",
                        "Non scendere mai sotto il 15% di margine, indipendentemente dal mercato.",
                        "shield-check", "green"
                    ),
                    strategy_card(
                        "Aggressive Undercut",
                        "Mantieni sempre il prezzo più basso del mercato di 0.50€.",
                        "zap", "red"
                    ),
                    strategy_card(
                        "Inventory Liquidation",
                        "Abbassa i prezzi per SKU con giacenza alta e basse vendite (dati GA4).",
                        "package", "orange"
                    ),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    spacing="6",
                    width="100%",
                ),

                rx.divider(margin_y="2rem"),

                # Pulsante di salvataggio
                rx.center(
                    rx.button(
                        rx.icon("save"), "Salva Configurazioni",
                        size="3", variant="solid", color_scheme="indigo",
                        width="300px"
                    ),
                    width="100%",
                ),

                spacing="7",
                width="100%",
                padding_y="2rem",
            ),
            max_width="1200px",
        ),
        bg="#F8FAFC",
        min_height="100vh",
    )