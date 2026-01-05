import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import csv
import json

from modules.auth import login_layout
from modules.home import dashboard_layout
from modules.operator_control import users_tab_layout, register_users_callbacks
from modules.location_database import locations_layout, register_locations_callbacks
from modules.system_alerts import notifications_layout, register_notifications_callbacks
from modules.route_configuration import routes_layout, register_routes_callbacks
from modules.path_optimizer import layout as find_routes_layout, register_find_routes_callbacks
from modules.analytics_dashboard import reports_layout, register_reports_callbacks

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.DARKLY,
        '/assets/custom.css'
    ],
)
app.title = "Campus Navigator Pro"

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="session-user", storage_type="session"),
    html.Div(id="page-content")
])

def read_users():
    try:
        with open("data/users.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        return [
            {"username": "admin", "password": "1234", "role": "admin"},
            {"username": "user1", "password": "abcd", "role": "user"},
        ]
    except Exception as e:
        print(f"Error reading users: {e}")
        return []

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    State("session-user", "data"),
)
def router(pathname, user_data):
    user = None
    if user_data:
        try:
            user = json.loads(user_data)
        except:
            user = None

    if not user:
        return login_layout()

    user_role = user.get('role', 'user')

    # Admin-only pages
    admin_pages = ['/dashboard/users', '/dashboard/locations', '/dashboard/routes', '/dashboard/reports']
    if pathname in admin_pages and user_role != 'admin':
        return dashboard_layout(user, content=html.Div([
            dbc.Alert([
                html.H4("Access Denied", className="alert-heading"),
                html.P("You don't have permission to access this page."),
                html.P("This section is only available for administrators.", className="mb-0")
            ], color="danger", className="mt-4")
        ]))

    if pathname == "/dashboard":
        return dashboard_layout(user)
    elif pathname == "/dashboard/users":
        return dashboard_layout(user, content=users_tab_layout())
    elif pathname == "/dashboard/locations":
        return dashboard_layout(user, content=locations_layout())
    elif pathname == "/dashboard/routes":
        return dashboard_layout(user, content=routes_layout())
    elif pathname == "/dashboard/find-routes":
        return dashboard_layout(user, content=find_routes_layout())
    elif pathname == "/dashboard/notifications":
        # Pass user to notifications callbacks + layout
        return dashboard_layout(user, content=notifications_layout(user_role))
    elif pathname == "/dashboard/reports":
        return dashboard_layout(user, content=reports_layout())

    # Fallback
    return dashboard_layout(user, content=html.Div("Page not found"))

@app.callback(
    Output("session-user", "data"),
    Output("url", "pathname"),
    Output("login-msg", "children"),
    Output("login-msg", "style"),
    Input("login-btn", "n_clicks"),
    State("operator_id", "value"),
    State("access_code", "value"),
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    if not n_clicks:
        return dash.no_update, dash.no_update, "", {"display": "none"}
    
    if not username or not password:
        return dash.no_update, dash.no_update, "Please enter username and password", {"display": "block", "color": "orange"}
    
    users = read_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            user_data = {"username": username, "role": user.get("role", "user")}
            return json.dumps(user_data), "/dashboard", "Login successful!", {"display": "block", "color": "lightgreen"}
    
    return dash.no_update, dash.no_update, "Invalid username or password", {"display": "block", "color": "orange"}

@app.callback(
    Output("session-user", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("logout-btn", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    if n_clicks:
        return None, "/"
    return dash.no_update, dash.no_update

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-dashboard", "n_clicks"),
    prevent_initial_call=True
)
def navigate_dashboard(n_clicks):
    if n_clicks:
        return "/dashboard"
    return dash.no_update

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-users", "n_clicks"),
    State("session-user", "data"),
    prevent_initial_call=True
)
def navigate_users(n_clicks, user_data):
    if n_clicks:
        user = json.loads(user_data) if user_data else None
        if user and user.get('role') == 'admin':
            return "/dashboard/users"
    return dash.no_update

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-locations", "n_clicks"),
    State("session-user", "data"),
    prevent_initial_call=True
)
def navigate_locations(n_clicks, user_data):
    if n_clicks:
        user = json.loads(user_data) if user_data else None
        if user and user.get('role') == 'admin':
            return "/dashboard/locations"
    return dash.no_update

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-routes", "n_clicks"),
    State("session-user", "data"),
    prevent_initial_call=True
)
def navigate_routes(n_clicks, user_data):
    if n_clicks:
        user = json.loads(user_data) if user_data else None
        if user and user.get('role') == 'admin':
            return "/dashboard/routes"
    return dash.no_update

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-find-routes", "n_clicks"),
    prevent_initial_call=True
)
def navigate_find_routes(n_clicks):
    if n_clicks:
        return "/dashboard/find-routes"
    return dash.no_update

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-reports", "n_clicks"),
    State("session-user", "data"),
    prevent_initial_call=True
)
def navigate_reports(n_clicks, user_data):
    if n_clicks:
        user = json.loads(user_data) if user_data else None
        if user and user.get('role') == 'admin':
            return "/dashboard/reports"
    return dash.no_update

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-notifications", "n_clicks"),
    State("session-user", "data"),
    prevent_initial_call=True
)
def navigate_notifications(n_clicks, user_data):
    if n_clicks:
        user = json.loads(user_data) if user_data else None
        if user:  # Any logged-in user can access notifications
            return "/dashboard/notifications"
    return dash.no_update

register_users_callbacks(app)
register_locations_callbacks(app)
register_routes_callbacks(app)
register_find_routes_callbacks(app)
register_notifications_callbacks(app)
register_reports_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
