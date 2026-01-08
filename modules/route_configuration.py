import os
import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

CSV_PATH = "data/routes.csv"
NOTIF_CSV_PATH = "data/notification.csv"
BLUE = "#2f80ed"

os.makedirs("data", exist_ok=True)

# ---------------- CSV Read / Write ----------------
def read_routes():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df["accessible"] = df["accessible"].apply(lambda x: True if str(x).lower() == "true" else False)
        return df
    return pd.DataFrame(columns=["id", "start_location", "end_location", "distance_m", "accessible"])

def save_routes(df):
    df.to_csv(CSV_PATH, index=False)

def add_notification(message, user_id=1):
    if os.path.exists(NOTIF_CSV_PATH):
        df = pd.read_csv(NOTIF_CSV_PATH)
    else:
        df = pd.DataFrame(columns=["id","user_id","message","delivered"])
    new_id = int(df.id.max()) + 1 if not df.empty else 1
    df = pd.concat([df, pd.DataFrame([{"id": new_id, "user_id": user_id, "message": message, "delivered": False}])], ignore_index=True)
    df.to_csv(NOTIF_CSV_PATH, index=False)

# ---------------- Table ----------------
def generate_table(df):
    if df.empty:
        return dbc.Card([
            dbc.CardBody([
                html.I(className="fas fa-route fa-3x text-muted mb-3"),
                html.H5("No Routes Found", className="text-muted"),
                html.P("Add your first route to get started!", className="text-muted mb-0")
            ])
        ], className="text-center py-5")

    header = html.Thead(html.Tr([
        html.Th([html.I(className="fas fa-hashtag me-2"), "ID"]),
        html.Th([html.I(className="fas fa-play-circle me-2"), "From"]),
        html.Th([html.I(className="fas fa-stop-circle me-2"), "To"]),
        html.Th([html.I(className="fas fa-ruler me-2"), "Distance"]),
        html.Th([html.I(className="fas fa-wheelchair me-2"), "Accessible"]),
        html.Th([html.I(className="fas fa-cogs me-2"), "Actions"])
    ]), className="table-dark")

    rows = []
    for _, r in df.iterrows():
        accessible_icon = "fas fa-check-circle text-success" if r.accessible else "fas fa-times-circle text-danger"
        accessible_text = "Yes" if r.accessible else "No"

        rows.append(html.Tr([
            html.Td(str(r.id), className="fw-semibold"),
            html.Td([
                html.I(className="fas fa-map-marker-alt text-primary me-2"),
                html.Span(r.start_location, className="fw-medium")
            ]),
            html.Td([
                html.I(className="fas fa-flag-checkered text-danger me-2"),
                html.Span(r.end_location, className="fw-medium")
            ]),
            html.Td([
                html.I(className="fas fa-route text-info me-2"),
                html.Span(f"{r.distance_m}m", className="fw-semibold")
            ]),
            html.Td([
                html.I(className=f"{accessible_icon} me-2"),
                html.Span(accessible_text, className="fw-semibold")
            ]),
            html.Td([
                dbc.Button([
                    html.I(className="fas fa-edit me-1"),
                    "Edit"
                ], id={"type":"edit","index":r.id}, size="sm", color="warning", className="me-2 btn-sm"),
                dbc.Button([
                    html.I(className="fas fa-trash me-1"),
                    "Delete"
                ], id={"type":"delete","index":r.id}, size="sm", color="danger", className="btn-sm")
            ])
        ]))

    return dbc.Table([header, html.Tbody(rows)], bordered=True, hover=True, striped=True, responsive=True, className="shadow-sm")

# ---------------- Layout ----------------
def routes_layout():
    df = read_routes()

    # Calculate statistics
    total_routes = len(df)
    accessible_routes = len(df[df.accessible == True]) if not df.empty else 0
    total_distance = df['distance_m'].sum() if not df.empty else 0
    avg_distance = df['distance_m'].mean() if not df.empty else 0

    return dbc.Container([
        html.H3([
            html.I(className="fas fa-route me-3 text-primary"),
            "Route Management"
        ], className="mb-4 text-primary fw-bold"),

        # Statistics Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-route fa-2x text-primary mb-2"),
                            html.H4(total_routes, className="mb-0 text-primary fw-bold"),
                            html.Small("Total Routes", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="shadow-sm mb-4")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-wheelchair fa-2x text-success mb-2"),
                            html.H4(accessible_routes, className="mb-0 text-success fw-bold"),
                            html.Small("Accessible Routes", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="shadow-sm mb-4")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-ruler fa-2x text-info mb-2"),
                            html.H4(f"{total_distance:.0f}m", className="mb-0 text-info fw-bold"),
                            html.Small("Total Distance", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="shadow-sm mb-4")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-chart-line fa-2x text-warning mb-2"),
                            html.H4(f"{avg_distance:.1f}m", className="mb-0 text-warning fw-bold"),
                            html.Small("Avg Distance", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="shadow-sm mb-4")
            ], md=3),
        ]),

        # Add/Edit Form
        dbc.Card(className="mb-4 shadow-lg", children=[
            dbc.CardHeader([
                html.I(className="fas fa-plus-circle me-2 text-success"),
                "Add New Route"
            ], className="bg-success text-white fw-bold"),
            dbc.CardBody([
                dcc.Store(id="edit-id", data=None),

                dbc.Row([
                    dbc.Col([
                        html.Label([
                            html.I(className="fas fa-play-circle me-2 text-primary"),
                            "Starting Location"
                        ], className="form-label fw-semibold"),
                        dcc.Input(
                            id="start",
                            placeholder="e.g., Main Gate, Library Entrance...",
                            className="form-control",
                            style={"borderRadius": "8px"}
                        )
                    ], md=6),
                    dbc.Col([
                        html.Label([
                            html.I(className="fas fa-stop-circle me-2 text-danger"),
                            "Ending Location"
                        ], className="form-label fw-semibold"),
                        dcc.Input(
                            id="end",
                            placeholder="e.g., Admin Building, Cafeteria...",
                            className="form-control",
                            style={"borderRadius": "8px"}
                        )
                    ], md=6),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col([
                        html.Label([
                            html.I(className="fas fa-ruler me-2 text-info"),
                            "Distance (meters)"
                        ], className="form-label fw-semibold"),
                        dcc.Input(
                            id="distance",
                            type="number",
                            placeholder="e.g., 150, 250, 500...",
                            className="form-control",
                            style={"borderRadius": "8px"}
                        )
                    ], md=6),
                    dbc.Col([
                        html.Label([
                            html.I(className="fas fa-wheelchair me-2 text-success"),
                            "Accessibility"
                        ], className="form-label fw-semibold"),
                        dcc.Dropdown(
                            id="accessible",
                            options=[
                                {"label": "🟢 Accessible Route (Wheelchair friendly)", "value": True},
                                {"label": "🔴 Not Accessible (Has stairs/obstacles)", "value": False},
                            ],
                            placeholder="Select route accessibility...",
                            style={"borderRadius": "8px", "color": "black"}
                        )
                    ], md=6),
                ], className="mb-4"),

                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-save me-2"),
                            "Save Route"
                        ], id="add-btn", color="success", size="lg", className="me-3 px-4"),
                        dbc.Button([
                            html.I(className="fas fa-undo me-2"),
                            "Reset Form"
                        ], id="reset-btn", color="secondary", size="lg", className="px-4"),
                    ], className="d-flex justify-content-center")
                ])
            ])
        ]),

        # Routes Table
        dbc.Card(className="shadow-lg", children=[
            dbc.CardHeader([
                html.I(className="fas fa-list me-2 text-primary"),
                f"All Routes ({total_routes})"
            ], className="bg-primary text-white fw-bold"),
            dbc.CardBody([
                html.Div(id="table", children=generate_table(df))
            ])
        ])
    ], fluid=True)

# ---------------- REGISTER CALLBACKS ----------------
def register_routes_callbacks(app):

    # ---------------- Add / Update / Reset ----------------
    @app.callback(
        Output("table","children", allow_duplicate=True),
        Output("start","value"),
        Output("end","value"),
        Output("distance","value"),
        Output("accessible","value"),
        Output("add-btn","children"),
        Output("edit-id","data"),
        Input("add-btn","n_clicks"),
        Input("reset-btn","n_clicks"),
        State("start","value"),
        State("end","value"),
        State("distance","value"),
        State("accessible","value"),
        State("edit-id","data"),
        prevent_initial_call=True
    )
    def add_update_reset(add_click, reset_click, s, e, d, a, edit_id):
        ctx = dash.callback_context
        trigger = ctx.triggered[0]["prop_id"]

        df = read_routes()

        # Reset
        if trigger == "reset-btn.n_clicks":
            return generate_table(df), "", "", None, None, "Add", None

        # Add / Update
        if not all([s,e]) or d is None or a is None:
            raise PreventUpdate

        if edit_id is not None:
            df.loc[df.id == edit_id, ["start_location","end_location","distance_m","accessible"]] = [s,e,d,a]
            add_notification(f"Route '{s} → {e}' updated")
        else:
            new_id = int(df.id.max())+1 if not df.empty else 1
            df = pd.concat([df, pd.DataFrame([{"id":new_id,"start_location":s,"end_location":e,"distance_m":d,"accessible":a}])], ignore_index=True)
            add_notification(f"New route '{s} → {e}' added")

        save_routes(df)
        return generate_table(df), "", "", None, None, "Add", None

    # ---------------- Edit ----------------
    @app.callback(
        Output("start","value", allow_duplicate=True),
        Output("end","value", allow_duplicate=True),
        Output("distance","value", allow_duplicate=True),
        Output("accessible","value", allow_duplicate=True),
        Output("add-btn","children", allow_duplicate=True),
        Output("edit-id","data", allow_duplicate=True),
        Input({"type":"edit","index":ALL},"n_clicks"),
        prevent_initial_call=True
    )
    def edit_route(clicks):
        if not any(clicks):
            raise PreventUpdate
        route_id = dash.callback_context.triggered_id["index"]
        df = read_routes()
        r = df[df.id==route_id].iloc[0]
        return r.start_location, r.end_location, r.distance_m, r.accessible, "Update", route_id

    # ---------------- Delete ----------------
    @app.callback(
        Output("table","children", allow_duplicate=True),
        Input({"type":"delete","index":ALL},"n_clicks"),
        prevent_initial_call=True
    )
    def delete_route(clicks):
        if not any(clicks):
            raise PreventUpdate
        route_id = dash.callback_context.triggered_id["index"]
        df = read_routes()
        df = df[df.id != route_id]
        save_routes(df)
        add_notification(f"Route {route_id} deleted")
        return generate_table(df)
