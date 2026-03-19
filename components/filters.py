import reflex as rx
from ..state import State

def filter_group(label: str, component: rx.Component):
    return rx.hstack(
        rx.text(label, size="2", weight="bold", color="slate-11"),
        component,
        align="center",
        spacing="2",
    )

def global_filter_bar():
    return rx.flex(
        filter_group("Brand:", rx.select.root(
            rx.select.trigger(),
            rx.select.content(rx.foreach(State.brands, lambda b: rx.select.item(b, value=b))),
            value=State.filter_brand, on_change=State.set_filter_brand,
        )),
        filter_group("Categoria:", rx.select.root(
            rx.select.trigger(),
            rx.select.content(rx.foreach(State.categories, lambda c: rx.select.item(c, value=c))),
            value=State.filter_category, on_change=State.set_filter_category,
        )),
        filter_group("Periodo:", rx.select.root(
            rx.select.trigger(),
            rx.select.content(rx.foreach(State.time_options, lambda t: rx.select.item(t, value=t))),
            value=State.filter_time, on_change=State.set_filter_time,
        )),
        filter_group("Cerca:", rx.input(
            placeholder="Nome prodotto...", on_change=State.set_search_product, width="200px"
        )),
        spacing="5", width="100%", bg="white", padding="1rem", border_radius="16px", box_shadow="sm", align="center", flex_wrap="wrap",
    )