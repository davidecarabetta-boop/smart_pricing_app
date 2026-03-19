import reflex as rx

# IMPORTANTE: I punti servono per la struttura a sottocartelle che hai
from .pages.home import home
from .pages.history import history
from .pages.strategie import strategie
from .pages.insights import insights
from .pages.data_center import data_center
from .pages.details import details
from .pages.insights import insights
from .pages.repricing_analysis import repricing_analysis
app = rx.App()

app.add_page(home, route="/")
app.add_page(history, route="/history")
app.add_page(strategie, route="/strategies")
app.add_page(insights, route="/insights")
app.add_page(data_center, route="/data_center")
app.add_page(details, route="/dettaglio")
app.add_page(repricing_analysis, route="/repricing_analysis")
app.add_page(insights, route="/insights")