import dash
import dash_bootstrap_components as dbc
from src.layout import create_layout
from src import callbacks # Import callbacks to register them

# Initialize the app with the CYBORG theme
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.CYBORG, "assets/custom_styles.css"],
    title="Media Analytics Dashboard",
    suppress_callback_exceptions=True
)

server = app.server

# Set the layout
app.layout = create_layout()

if __name__ == '__main__':
    app.run(debug=True, port=8050)
