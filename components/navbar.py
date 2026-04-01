import reflex as rx

def navbar_link(text: str, url: str):
    return rx.link(rx.text(text, font_weight="500", color="#5F6368"), href=url, _hover={"color": "#1A73E8"})

def navbar():
    return rx.box(
        rx.hstack(
            rx.hstack(rx.icon(tag="chart-candlestick", color="#1A73E8"), rx.heading("SmartPricing Pro", size="6")),
            rx.spacer(),
            rx.hstack(
                navbar_link("Dashboard", "/"),
                navbar_link("Strategie", "/strategies"),
                navbar_link("Insights", "/insights"),
                navbar_link("Data Center", "/data_center"),
                navbar_link("Impostazioni", "/settings"),
                spacing="5", align_items="center",
            ),
            padding_x="40px", padding_y="15px", width="100%", align_items="center",
        ),
        bg="white", border_bottom="1px solid #E0E0E0", width="100%", position="sticky", top="0", z_index="1000",
    )