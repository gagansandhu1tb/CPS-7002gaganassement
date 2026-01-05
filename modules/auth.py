import csv
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


def load_user_database():
    with open("data/users.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def login_layout():
    return dbc.Container(
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Login", className="text-center fw-bold fs-4 py-3 bg-dark text-light"),
                    dbc.CardBody([
                        dbc.Input(id="operator_id", placeholder="Username", className="mb-3 form-control-lg"),
                        dbc.Input(id="access_code", placeholder="Password", type="password", className="mb-4 form-control-lg"),
                        dbc.Button("Login", id="login-btn", color="dark", className="w-100 py-2 fw-semibold fs-5"),
                        html.Div(id="login-msg", className="text-warning mt-3 text-center fw-semibold")
                    ], className="px-4 py-3")
                ], className="shadow-lg border-0 bg-secondary text-light"),
                width=5
            ),
            justify="center",
            align="center",
            className="vh-100 bg-dark"
        ),
        fluid=True,
        className="bg-dark"
    )


def login_callback(app):

    @app.callback(
        Output("session-user", "data"),
        Output("login-msg", "children"),
        Input("login-btn", "n_clicks"),
        State("operator_id", "value"),
        State("access_code", "value"),
        prevent_initial_call=True
    )
    def authenticate_user(n, username, password):

        if not username or not password:
            return None, "Enter username & password"

        for user in load_user_database():
            if user["username"] == username and user["password"] == password:
                if user["status"] != "active":
                    return None, "Account inactive"

                return {
                    "username": user["username"],
                    "full_name": user["full_name"],
                    "email": user["email"],
                    "role": user["role"],
                    "status": user["status"],
                }, ""

        return None, "Invalid username or password"
