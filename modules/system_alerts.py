import os
import dash
import pandas as pd
import json
from dash import html, dcc, Input, Output, State
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# ------------------ Config ------------------
NOTIF_CSV_PATH = "data/notification.csv"
BLUE = "#2f80ed"

# ------------------ CSV Read / Write ------------------
def read_notifications():
    if os.path.exists(NOTIF_CSV_PATH):
        df = pd.read_csv(NOTIF_CSV_PATH)
        df["delivered"] = df["delivered"].apply(lambda x: True if str(x).lower() == "true" else False)
        return df
    return pd.DataFrame(columns=["id", "user_id", "message", "delivered"])

def save_notifications(df):
    df.to_csv(NOTIF_CSV_PATH, index=False)

# ------------------ Table ------------------
def generate_notifications_table(df, user_role="student"):
    header = html.Tr([
        html.Th("ID", className="p-2 bg-light border"),
        html.Th("User ID", className="p-2 bg-light border"),
        html.Th("Message", className="p-2 bg-light border"),
        html.Th("Delivered", className="p-2 bg-light border"),
        html.Th("Actions", className="p-2 bg-light border"),
    ])

    rows = []
    is_disabled = user_role != "admin"

    for _, row in df.iterrows():
        row_data = [
            html.Td(row.id, className="p-2 border"),
            html.Td(row.user_id, className="p-2 border"),
            html.Td(row.message, className="p-2 border"),
            html.Td(
                "Yes" if row.delivered else "No",
                style={"color": BLUE if row.delivered else "red", "fontWeight": "bold"},
                className="p-2 border"
            ),
            html.Td([
                dbc.Button(
                    "Edit",
                    id={"type": "edit-notif", "index": int(row.id)},
                    size="sm",
                    className="me-1",
                    disabled=is_disabled
                ),
                dbc.Button(
                    "Delete",
                    id={"type": "delete-notif", "index": int(row.id)},
                    size="sm",
                    color="danger",
                    disabled=is_disabled
                )
            ])
        ]
        rows.append(html.Tr(row_data))

    return dbc.Table([header] + rows, hover=True, striped=True, responsive=True, className="mb-0 shadow-sm")

# ------------------ Layout ------------------
def notifications_layout(user_role="student"):
    df = read_notifications()
    is_disabled = user_role != "admin"

    return dbc.Container(fluid=True, children=[
        html.H3("Notifications", className="mb-4 text-primary fw-bold"),

        # ================= FORM =================
        dbc.Card(
            className="mb-4 shadow-sm",
            children=[
                dbc.CardBody([
                    html.H4("Add / Edit Notification", className="mb-3"),
                    dcc.Store(id="edit-notif-id"),

                    dbc.Row([
                        dbc.Col(
                            dcc.Input(
                                id="notif-user-id",
                                type="number",
                                placeholder="User ID",
                                className="form-control",
                                disabled=is_disabled
                            ),
                            md=3
                        ),
                        dbc.Col(
                            dcc.Input(
                                id="notif-message",
                                placeholder="Message",
                                className="form-control",
                                disabled=is_disabled
                            ),
                            md=6
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="notif-delivered",
                                options=[
                                    {"label": "Delivered", "value": True},
                                    {"label": "Not Delivered", "value": False}
                                ],
                                placeholder="Delivered",
                                disabled=is_disabled
                            ),
                            md=3
                        )
                    ], className="mb-3"),

                    dbc.Row(className="justify-content-end", children=[
                        dbc.Col(
                            dbc.Button("Add", id="add-notif-btn", color="primary", className="me-2", disabled=is_disabled),
                            width="auto"
                        ),
                        dbc.Col(
                            dbc.Button("Reset", id="reset-notif-btn", color="secondary", disabled=is_disabled),
                            width="auto"
                        )
                    ])
                ])
            ]
        ),

        # ================= TABLE =================
        dbc.Card(className="p-3 shadow-sm", children=[
            dcc.Input(
                id="search-notif",
                placeholder="Search notifications...",
                className="form-control mb-3",
                style={"maxWidth": "300px"}
            ),
            html.Div(
                id="table-notif",
                children=generate_notifications_table(df, user_role)
            )
        ])
    ])

# ------------------ Callbacks ------------------
def register_notifications_callbacks(app):
    # ------------------ Delete ------------------
    @app.callback(
        Output("table-notif", "children", allow_duplicate=True),
        Input({"type": "delete-notif", "index": ALL}, "n_clicks"),
        State("session-user", "data"),
        prevent_initial_call=True
    )
    def delete_notification(clicks, user_data):
        user = json.loads(user_data) if user_data else None
        user_role = user.get("role", "student") if user else "student"
        if user_role != "admin" or not any(clicks):
            raise PreventUpdate

        ctx = dash.callback_context
        notif_id = eval(ctx.triggered[0]["prop_id"].split(".")[0])["index"]

        df = read_notifications()
        df = df[df.id != notif_id]
        save_notifications(df)

        return generate_notifications_table(df, user_role)

    # ------------------ Edit / Reset ------------------
    @app.callback(
        Output("notif-user-id", "value"),
        Output("notif-message", "value"),
        Output("notif-delivered", "value"),
        Output("add-notif-btn", "children"),
        Output("edit-notif-id", "data"),
        Input({"type": "edit-notif", "index": ALL}, "n_clicks"),
        Input("reset-notif-btn", "n_clicks"),
        State("session-user", "data"),
        prevent_initial_call=True
    )
    def handle_edit_reset(edit_clicks, reset_click, user_data):
        user = json.loads(user_data) if user_data else None
        user_role = user.get("role", "student") if user else "student"
        if user_role != "admin":
            raise PreventUpdate

        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered[0]["prop_id"]
        if trigger == "reset-notif-btn.n_clicks":
            return None, "", None, "Add", None

        notif_id = eval(trigger.split(".")[0])["index"]
        df = read_notifications()
        r = df[df.id == notif_id].iloc[0]
        return r.user_id, r.message, r.delivered, "Update", notif_id

    # ------------------ Add / Update ------------------
    @app.callback(
        Output("table-notif", "children", allow_duplicate=True),
        Input("add-notif-btn", "n_clicks"),
        State("notif-user-id", "value"),
        State("notif-message", "value"),
        State("notif-delivered", "value"),
        State("edit-notif-id", "data"),
        State("session-user", "data"),
        prevent_initial_call=True
    )
    def save_notification(_, user_id, message, delivered, edit_id, user_data):
        user = json.loads(user_data) if user_data else None
        user_role = user.get("role", "student") if user else "student"
        if user_role != "admin" or user_id is None or not message or delivered is None:
            raise PreventUpdate

        df = read_notifications()
        if edit_id is not None:
            df.loc[df.id == edit_id, ["user_id", "message", "delivered"]] = [user_id, message, delivered]
        else:
            new_id = int(df.id.max()) + 1 if not df.empty else 1
            df = pd.concat([df, pd.DataFrame([{"id": new_id, "user_id": user_id, "message": message, "delivered": delivered}])], ignore_index=True)

        save_notifications(df)
        return generate_notifications_table(df, user_role)

    # ------------------ Search ------------------
    @app.callback(
        Output("table-notif", "children", allow_duplicate=True),
        Input("search-notif", "value"),
        State("session-user", "data"),
        prevent_initial_call=True
    )
    def search_notifications(text, user_data):
        user = json.loads(user_data) if user_data else None
        user_role = user.get("role", "student") if user else "student"
        df = read_notifications()
        if not text:
            return generate_notifications_table(df, user_role)
        t = text.lower()
        df = df[df.apply(lambda r: t in str(r).lower(), axis=1)]
        return generate_notifications_table(df, user_role)
