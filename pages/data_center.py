import reflex as rx
from ..components.navbar import navbar

def data_center():
    return rx.vstack(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Data Center", size="8", weight="bold"),
                rx.upload(rx.vstack(rx.icon(tag="upload", size=40), rx.text("Carica listino CSV/Excel"), padding="3rem"), border="2px dashed #E5E7EB", border_radius="16px", width="100%"),
                rx.heading("Sorgenti Collegate", size="4", margin_top="2rem"),
                rx.badge("Amazon API: Connesso", color_scheme="green", variant="soft"),
                width="100%", spacing="5", padding_y="2rem",
            ),
        ),
        bg="#F8FAFC", min_height="100vh",
    )