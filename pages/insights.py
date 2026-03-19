import reflex as rx
from ..state import State
from ..components.navbar import navbar
from ..components.filters import global_filter_bar # Importiamo il componente unico

def insights():
    return rx.vstack(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Analisi Approfondita", size="8", weight="bold"),
                rx.text("Monitora la salute del tuo catalogo e il market share.", color="gray"),

                # --- BARRA DEI FILTRI GLOBALE ---
                global_filter_bar(), #

                rx.grid(
                    # --- BOX 1: DISTRIBUZIONE CATEGORIE (PIE CHART) ---
                    rx.vstack(
                        rx.heading("Mix Categorie", size="4"),
                        rx.recharts.pie_chart(
                            rx.recharts.pie(
                                data=State.category_data,
                                data_key="value",
                                name_key="name",
                                cx="50%",
                                cy="50%",
                                outer_radius=80,
                                label=True,
                            ),
                            rx.recharts.graphing_tooltip(), #
                            rx.recharts.legend(),
                            width="100%",
                            height=300,
                        ),
                        bg="white", padding="1.5rem", border_radius="16px", box_shadow="sm",
                    ),

                    # --- BOX 2: CONFRONTO MARKET SHARE (BAR CHART) ---
                    rx.vstack(
                        rx.heading("Posizionamento vs Competitor", size="4"),
                        rx.recharts.bar_chart(
                            rx.recharts.bar(
                                data_key="price", fill="#2563EB", name="Tuo Prezzo", radius=[4, 4, 0, 0]
                            ),
                            rx.recharts.x_axis(data_key="name"),
                            rx.recharts.y_axis(),
                            rx.recharts.graphing_tooltip(),
                            rx.recharts.legend(),
                            data=State.market_position_data,
                            width="100%",
                            height=300,
                        ),
                        bg="white", padding="1.5rem", border_radius="16px", box_shadow="sm",
                    ),

                    columns=rx.breakpoints(initial="1", lg="2"),
                    spacing="4",
                    width="100%",
                ),

                # --- BOX 3: SUGGERIMENTI AI ---
                rx.box(
                    rx.hstack(
                        rx.icon("lightbulb", color="#EAB308"),
                        rx.vstack(
                            rx.text("Suggerimento AI", weight="bold"),
                            rx.text(
                                "Il brand 'Dior' ha un Price Index molto alto (108). Considera uno sconto del 3% per riprendere volumi.",
                                size="2"),
                            align_items="start",
                        ),
                        spacing="3",
                    ),
                    bg="#FEFCE8", padding="1.5rem", border_radius="16px", border="1px solid #FEF08A", width="100%",
                ),

                spacing="6",
                width="100%",
                padding_y="2rem",
            ),
            max_width="1200px",
        ),
        bg="#F8FAFC",
        min_height="100vh",
    )