from dash import html, dcc, Input, Output, State, ctx, ALL
import dash_bootstrap_components as dbc
import dash
import csv
import os
import uuid

# ---------------- ENSURE DATA FOLDER ----------------
os.makedirs("data", exist_ok=True)
CSV_PATH = "data/users.csv"

FIELDS = ["id", "username", "password", "full_name", "email", "role", "status"]

# ---------------- READ USERS ----------------
def read_users():
    if not os.path.exists(CSV_PATH):
        admin = [{
            "id": str(uuid.uuid4()),
            "username": "admin",
            "password": "1234",
            "full_name": "Admin User",
            "email": "admin@test.com",
            "role": "admin",
            "status": "active",
        }]
        write_users(admin)
        return admin

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

# ---------------- WRITE USERS ----------------
def write_users(users):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(users)

# ---------------- LAYOUT ----------------
def users_tab_layout():
    # Initialize with users data
    users = read_users()
    return dbc.Container([
        # Header Section
        dbc.Row([
            dbc.Col([
                html.H2("User Management", className="text-light mb-4 fw-bold"),
                html.P("Manage users and access permissions", className="text-muted mb-4"),
            ], width=8),
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-plus-circle me-2"), "Add User"],
                    id="add-user-btn",
                    color="outline-light",
                    className="w-100 py-3 fw-semibold border-2"
                ),
            ], width=4, className="d-flex align-items-center")
        ], className="mb-4"),

        # Statistics Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-users fa-2x text-info mb-2"),
                            html.H4(len([u for u in users if u["status"] == "active"]), className="text-info mb-0 fw-bold"),
                            html.Small("Active Users", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="bg-secondary border-0 shadow-sm stats-card")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-user-shield fa-2x text-warning mb-2"),
                            html.H4(len([u for u in users if u["role"] == "admin"]), className="text-warning mb-0 fw-bold"),
                            html.Small("Admins", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="bg-secondary border-0 shadow-sm stats-card")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-user-graduate fa-2x text-success mb-2"),
                            html.H4(len([u for u in users if u["role"] == "student"]), className="text-success mb-0 fw-bold"),
                            html.Small("Students", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="bg-secondary border-0 shadow-sm stats-card")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-user-tie fa-2x text-primary mb-2"),
                            html.H4(len([u for u in users if u["role"] == "staff"]), className="text-primary mb-0 fw-bold"),
                            html.Small("Staff", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="bg-secondary border-0 shadow-sm stats-card")
            ], width=3),
        ], className="mb-4"),

        # Operators Grid
        html.Div(id="operators-grid-container", className="row"),

        # Registration Modal
        dbc.Modal([
            dbc.ModalHeader([
                html.I(className="fas fa-user-plus me-2 text-info"),
                dbc.ModalTitle(id="operator-modal-title", className="fw-bold")
            ], className="bg-dark text-light"),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Username", className="form-label fw-semibold text-light"),
                        dbc.Input(id="user-username", placeholder="Enter username", className="mb-3 bg-secondary border-secondary text-light"),
                    ], md=6),
                    dbc.Col([
                        html.Label("Password", className="form-label fw-semibold text-light"),
                        dbc.Input(id="user-password", type="password", placeholder="Enter password", className="mb-3 bg-secondary border-secondary text-light"),
                    ], md=6),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Label("Full Name", className="form-label fw-semibold text-light"),
                        dbc.Input(id="user-fullname", placeholder="Enter full name", className="mb-3 bg-secondary border-secondary text-light"),
                    ], md=6),
                    dbc.Col([
                        html.Label("Email", className="form-label fw-semibold text-light"),
                        dbc.Input(id="user-email", type="email", placeholder="Enter email address", className="mb-3 bg-secondary border-secondary text-light"),
                    ], md=6),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Label("Role", className="form-label fw-semibold text-light"),
                        dbc.Select(
                            id="user-role",
                            options=[
                                {"label": "Student", "value": "student"},
                                {"label": "Visitor", "value": "visitor"},
                                {"label": "Staff", "value": "staff"},
                                {"label": "Admin", "value": "admin"}
                            ],
                            value="student",
                            className="mb-3 bg-secondary border-secondary text-light"
                        ),
                    ], md=6),
                    dbc.Col([
                        html.Label("Status", className="form-label fw-semibold text-light"),
                        dbc.Select(
                            id="user-status",
                            options=[
                                {"label": "Active", "value": "active"},
                                {"label": "Inactive", "value": "inactive"}
                            ],
                            value="active",
                            className="mb-3 bg-secondary border-secondary text-light"
                        ),
                    ], md=6),
                ]),
            ], className="bg-dark"),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-user-btn", className="me-2", color="secondary"),
                dbc.Button([
                    html.I(className="fas fa-save me-2"),
                    "Save"
                ], id="save-user-btn", color="info", className="px-4"),
            ], className="bg-dark border-secondary")
        ], id="user-modal", is_open=False, size="lg", className="modal-dark"),

        dcc.Store(id="users-data", data=users),
        dcc.Store(id="editing-user-index"),
    ], fluid=True)

# ---------------- CALLBACKS ----------------
def register_users_callbacks(app):

    # -------- OPERATORS GRID RENDER --------
    @app.callback(
        Output("operators-grid-container", "children"),
        Input("users-data", "data")
    )
    def render_operators_grid(users):
        if not users:
            return dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-users fa-3x text-muted mb-3"),
                            html.H5("No Operators Found", className="text-muted"),
                            html.P("Register your first operator to begin system management", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], className="bg-secondary border-0 shadow-sm")
            ], width=12)

        cards = []
        role_colors = {
            "admin": "warning",
            "staff": "primary",
            "student": "success",
            "visitor": "info"
        }

        status_icons = {
            "active": "fas fa-circle text-success",
            "inactive": "fas fa-circle text-danger"
        }

        for user in users:
            role_color = role_colors.get(user["role"], "secondary")
            status_icon = status_icons.get(user["status"], "fas fa-circle text-secondary")

            card = dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-user-circle fa-lg me-2 text-info"),
                            html.Span(user["username"], className="fw-bold text-light"),
                            html.Span([
                                html.I(className=f"{status_icon} ms-2"),
                                html.Small(user["status"].title(), className="ms-1 text-muted")
                            ], className="float-end")
                        ], className="d-flex justify-content-between align-items-center bg-dark text-light border-0")
                    ]),
                    dbc.CardBody([
                        html.Div([
                            html.P([
                                html.I(className="fas fa-id-badge me-2 text-muted"),
                                html.Strong("Name: ", className="text-light"),
                                html.Span(user["full_name"], className="text-light")
                            ], className="mb-2"),
                            html.P([
                                html.I(className="fas fa-envelope me-2 text-muted"),
                                html.Strong("Email: ", className="text-light"),
                                html.Span(user["email"], className="text-light")
                            ], className="mb-3"),
                            html.Div([
                                dbc.Badge(
                                    user["role"].title(),
                                    color=role_color,
                                    className="me-2 px-3 py-2"
                                ),
                            ], className="mb-3")
                        ]),
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-edit me-1"),
                                "Edit"
                            ], id={"type": "edit-user", "id": user["id"]},
                            color="outline-warning", size="sm", className="me-2"),
                            dbc.Button([
                                html.I(className="fas fa-trash-alt me-1"),
                                "Delete"
                            ], id={"type": "delete-user", "id": user["id"]},
                            color="outline-danger", size="sm")
                        ], className="d-flex justify-content-end")
                    ])
                ], className="bg-secondary border-0 shadow-sm h-100 operator-card")
            ], width=12, md=6, lg=4, xl=3, className="mb-4")

            cards.append(card)

        return cards

    # -------- MODAL & CONTROLLER --------
    @app.callback(
        Output("users-data", "data"),
        Output("user-modal", "is_open"),
        Output("operator-modal-title", "children"),
        Output("editing-user-index", "data"),
        Output("user-username", "value"),
        Output("user-username", "disabled"),
        Output("user-password", "value"),
        Output("user-fullname", "value"),
        Output("user-email", "value"),
        Output("user-role", "value"),
        Output("user-status", "value"),
        Input("add-user-btn", "n_clicks"),
        Input({"type": "edit-user", "id": ALL}, "n_clicks"),
        Input("cancel-user-btn", "n_clicks"),
        Input("save-user-btn", "n_clicks"),
        Input({"type": "delete-user", "id": ALL}, "n_clicks"),
        State("editing-user-index", "data"),
        State("users-data", "data"),
        State("user-username", "value"),
        State("user-password", "value"),
        State("user-fullname", "value"),
        State("user-email", "value"),
        State("user-role", "value"),
        State("user-status", "value"),
        prevent_initial_call=False
    )
    def controller(add, edit, cancel, save, delete,
                   index, users, username, password, fullname, email, role, status):

        trig = ctx.triggered_id

        # If no users data, initialize (shouldn't happen with initialized store)
        if users is None:
            users = read_users()

        # -------- CANCEL --------
        if trig == "cancel-user-btn":
            return users, False, "", None, "", False, "", "", "", "student", "active"

        # -------- ADD NEW USER --------
        if trig == "add-user-btn":
            return users, True, "Add User", None, "", False, "", "", "", "student", "active"

        # -------- EDIT USER --------
        if isinstance(trig, dict) and trig.get("type") == "edit-user":
            for i, u in enumerate(users):
                if u["id"] == trig["id"]:
                    return (
                        users, True, "Edit User", i,
                        u["username"], True,
                        "", u["full_name"], u["email"], u["role"], u["status"]
                    )

        # -------- SAVE USER --------
        if trig == "save-user-btn":
            if index is None:
                users.append({
                    "id": str(uuid.uuid4()),
                    "username": username,
                    "password": password,
                    "full_name": fullname,
                    "email": email,
                    "role": role,
                    "status": status
                })
            else:
                u = users[index]
                u.update({
                    "full_name": fullname,
                    "email": email,
                    "role": role,
                    "status": status
                })
                if password:
                    u["password"] = password
            write_users(users)
            return users, False, "", None, "", False, "", "", "", "student", "active"

        # -------- DELETE USER --------
        if isinstance(trig, dict) and trig.get("type") == "delete-user":
            users = [u for u in users if u["id"] != trig["id"]]
            write_users(users)
            return users, False, "", None, "", False, "", "", "", "student", "active"

        # If no trigger (initial load), just return current data
        return users, False, "", None, "", False, "", "", "", "student", "active"
