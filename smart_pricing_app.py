import reflex as rx
from .state import State

from .pages.home import home
from .pages.brand import brand_page
from .pages.data_center import data_center
from .pages.details import details
from .pages.settings import settings

app = rx.App()

app.add_page(home, route="/", on_load=State.on_load)
app.add_page(brand_page, route="/brand", on_load=State.on_load)
app.add_page(data_center, route="/data_center", on_load=State.on_load)
app.add_page(details, route="/dettaglio", on_load=State.on_load)
app.add_page(settings, route="/settings", on_load=State.on_load)