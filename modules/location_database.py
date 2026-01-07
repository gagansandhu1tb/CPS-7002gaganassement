import os
import pandas as pd
import dash
from dash import html, dcc, Input, Output, State
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# ------------------ Config ------------------
CSV_PATH = "data/locations.csv"
os.makedirs("data", exist_ok=True)

# ------------------ CSV Read / Write ------------------
def read_locations():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)

        # FIX boolean from CSV
        df["accessible"] = df["accessible"].apply(
            lambda x: True if str(x).lower() == "true" else False
        )

        return df

    return pd.DataFrame(columns=["id", "name", "building", "floor", "accessible"])


def save_locations(df):
    df.to_csv(CSV_PATH, index=False)

# ------------------ Table ------------------
def generate_locations_table(df):
    if df.empty:
        return dbc.Card([
            dbc.CardBody([
                html.I(className="fas fa-map-marker-alt fa-3x text-muted mb-3"),
                html.H5("No Locations Found", className="text-muted"),
                html.P("Add your first location to get started!", className="text-muted mb-0")
            ])
        ], className="text-center py-5")

    header = html.Thead(html.Tr([
        html.Th([html.I(className="fas fa-hashtag me-2"), "ID"]),
        html.Th([html.I(className="fas fa-tag me-2"), "Name"]),
        html.Th([html.I(className="fas fa-building me-2"), "Building"]),
        html.Th([html.I(className="fas fa-layer-group me-2"), "Floor"]),
        html.Th([html.I(className="fas fa-wheelchair me-2"), "Accessible"]),
        html.Th([html.I(className="fas fa-cogs me-2"), "Actions"]),
    ]), className="table-dark")

    rows = []
    for _, row in df.iterrows():
        accessible_icon = "fas fa-check-circle text-success" if row.accessible else "fas fa-times-circle text-danger"
        accessible_text = "Yes" if row.accessible else "No"

        rows.append(html.Tr([
            html.Td(str(row.id), className="fw-semibold"),
            html.Td([
                html.I(className="fas fa-map-pin text-primary me-2"),
                html.Span(row.name, className="fw-medium")
            ]),
            html.Td([
                html.I(className="fas fa-building text-info me-2"),
                html.Span(row.building, className="fw-medium")
            ]),
            html.Td([
                html.I(className="fas fa-layer-group text-secondary me-2"),
                html.Span(row.floor, className="fw-medium")
            ]),
            html.Td([
                html.I(className=f"{accessible_icon} me-2"),
                html.Span(accessible_text, className="fw-semibold")
            ]),
            html.Td([
                dbc.Button([
                    html.I(className="fas fa-edit me-1"),
                    "Edit"
                ], id={"type": "edit-loc", "index": row.id}, size="sm", color="warning", className="me-2 btn-sm"),
                dbc.Button([
                    html.I(className="fas fa-trash me-1"),
                    "Delete"
                ], id={"type": "delete-loc", "index": row.id}, size="sm", color="danger", className="btn-sm")
            ])
        ]))

    return dbc.Table(
        [header, html.Tbody(rows)],
        bordered=True,
        hover=True,
        striped=True,
        responsive=True,
        className="shadow-sm"
    )

# ------------------ Layout ------------------
def locations_layout():
    df = read_locations()

    # Calculate statistics
    total_locations = len(df)
    accessible_count = len(df[df.accessible == True]) if not df.empty else 0
    buildings = df['building'].nunique() if not df.empty else 0

    return dbc.Container(fluid=True, children=[
        html.H3([
            html.I(className="fas fa-map-marked-alt me-3 text-primary"),
            "Location Management"
        ], className="mb-4 text-primary fw-bold"),

        # Statistics Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-map-marker-alt fa-2x text-primary mb-2"),
                            html.H4(total_locations, className="mb-0 text-primary fw-bold"),
                            html.Small("Total Locations", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="shadow-sm mb-4")
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-wheelchair fa-2x text-success mb-2"),
                            html.H4(accessible_count, className="mb-0 text-success fw-bold"),
                            html.Small("Accessible Locations", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="shadow-sm mb-4")
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-building fa-2x text-info mb-2"),
                            html.H4(buildings, className="mb-0 text-info fw-bold"),
                            html.Small("Buildings", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="shadow-sm mb-4")
            ], md=4),
        ]),

        # Add/Edit Form
        dbc.Card(className="mb-4 shadow-lg", children=[
            dbc.CardHeader([
                html.I(className="fas fa-plus-circle me-2 text-success"),
                "Add New Location"
            ], className="bg-success text-white fw-bold"),
            dbc.CardBody([
                dcc.Store(id="edit-loc-id"),

                dbc.Row([
                    dbc.Col([
                        html.Label([
                            html.I(className="fas fa-tag me-2 text-primary"),
                            "Location Name"
                        ], className="form-label fw-semibold"),
                        dcc.Input(
                            id="loc-name",
                            placeholder="e.g., Main Library, Cafeteria, Admin Office...",
                            className="form-control",
                            style={"borderRadius": "8px"}
                        )
                    ], md=6),
                    dbc.Col([
                        html.Label([
                            html.I(className="fas fa-building me-2 text-info"),
                            "Building"
                        ], className="form-label fw-semibold"),
                        dcc.Input(
                            id="loc-building",
                            placeholder="e.g., Academic Block, Library Building...",
                            className="form-control",
                            style={"borderRadius": "8px"}
                        )
                    ], md=6),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col([
                        html.Label([
                            html.I(className="fas fa-layer-group me-2 text-secondary"),
                            "Floor"
                        ], className="form-label fw-semibold"),
                        dcc.Input(
                            id="loc-floor",
                            placeholder="e.g., Ground, 1st, 2nd...",
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
                            id="loc-accessible",
                            options=[
                                {"label": "🟢 Accessible (Wheelchair friendly)", "value": True},
                                {"label": "🔴 Not Accessible", "value": False},
                            ],
                            placeholder="Select accessibility status...",
                            style={"borderRadius": "8px", "color": "black"}
                        )
                    ], md=6),
                ], className="mb-4"),

                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-save me-2"),
                            "Save Location"
                        ], id="add-loc-btn", color="success", size="lg", className="me-3 px-4"),
                        dbc.Button([
                            html.I(className="fas fa-undo me-2"),
                            "Reset Form"
                        ], id="reset-loc-btn", color="secondary", size="lg", className="px-4"),
                    ], className="d-flex justify-content-center")
                ])
            ])
        ]),

        # Locations Table
        dbc.Card(className="shadow-lg", children=[
            dbc.CardHeader([
                html.I(className="fas fa-list me-2 text-primary"),
                f"All Locations ({total_locations})"
            ], className="bg-primary text-white fw-bold"),
            dbc.CardBody([
                html.Div(id="table-loc", children=generate_locations_table(df))
            ])
        ])

    ])

# ======================================================
# REGISTER CALLBACKS (REGISTER ONCE IN main.py)
# ======================================================
def register_locations_callbacks(app):

    # ------------------ DELETE ------------------
    @app.callback(
        Output("table-loc", "children", allow_duplicate=True),
        Input({"type": "delete-loc", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def delete_location(clicks):
        if not any(clicks):
            raise PreventUpdate

        ctx = dash.callback_context
        loc_id = ctx.triggered_id["index"]

        df = read_locations()
        df = df[df.id != loc_id]
        save_locations(df)

        return generate_locations_table(df)

    # ------------------ EDIT + RESET (SINGLE CALLBACK) ------------------
    @app.callback(
        Output("loc-name", "value"),
        Output("loc-building", "value"),
        Output("loc-floor", "value"),
        Output("loc-accessible", "value"),
        Output("add-loc-btn", "children"),
        Output("edit-loc-id", "data"),
        Input({"type": "edit-loc", "index": ALL}, "n_clicks"),
        Input("reset-loc-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def handle_edit_reset(edit_clicks, reset_click):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered[0]["prop_id"]

        # -------- RESET --------
        if trigger == "reset-loc-btn.n_clicks":
            return "", "", "", None, "Add", None

        # -------- EDIT --------
        loc_id = ctx.triggered_id["index"]
        df = read_locations()
        row = df[df.id == loc_id].iloc[0]

        return (
            row.name,
            row.building,
            row.floor,
            row.accessible,
            "Update",
            loc_id
        )

    # ------------------ ADD / UPDATE ------------------
    @app.callback(
        Output("table-loc", "children", allow_duplicate=True),
        Input("add-loc-btn", "n_clicks"),
        State("loc-name", "value"),
        State("loc-building", "value"),
        State("loc-floor", "value"),
        State("loc-accessible", "value"),
        State("edit-loc-id", "data"),
        prevent_initial_call=True
    )
    def save_location(_, name, building, floor, accessible, edit_id):
        if not name or not building or not floor or accessible is None:
            raise PreventUpdate

        df = read_locations()

        if edit_id is not None:
            df.loc[df.id == edit_id, ["name", "building", "floor", "accessible"]] = [
                name, building, floor, accessible
            ]
        else:
            new_id = int(df.id.max()) + 1 if not df.empty else 1
            df = pd.concat([
                df,
                pd.DataFrame([{
                    "id": new_id,
                    "name": name,
                    "building": building,
                    "floor": floor,
                    "accessible": accessible
                }])
            ], ignore_index=True)

        save_locations(df)
        return generate_locations_table(df)
