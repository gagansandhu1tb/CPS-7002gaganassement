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
    return html.Div([
        html.H3("👥 Users Management", className="mb-4"),

        html.Div(id="users-table-container"),

        dbc.Button("➕ Add User", id="add-user-btn", color="primary", className="me-2"),

        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="user-modal-title")),
            dbc.ModalBody([
                dbc.Input(id="user-username", placeholder="Username", className="mb-2"),
                dbc.Input(id="user-password", type="password", placeholder="Password", className="mb-2"),
                dbc.Input(id="user-fullname", placeholder="Full Name", className="mb-2"),
                dbc.Input(id="user-email", type="email", placeholder="Email", className="mb-2"),
                dbc.Select(
                    id="user-role",
                    options=[
                        {"label": "Student", "value": "student"},
                        {"label": "Visitor", "value": "visitor"},
                        {"label": "Staff", "value": "staff"},
                        {"label": "Admin", "value": "admin"}
                    ],
                    value="student",
                    className="mb-2"
                ),
                dbc.Select(
                    id="user-status",
                    options=[{"label": "Active", "value": "active"}, {"label": "Inactive", "value": "inactive"}],
                    value="active"
                ),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-user-btn", className="me-2"),
                dbc.Button("Save", id="save-user-btn", color="primary"),
            ])
        ], id="user-modal", is_open=False),

        dcc.Store(id="users-data", data=users),  # Initialize with data
        dcc.Store(id="editing-user-index"),
    ])

# ---------------- CALLBACKS ----------------
def register_users_callbacks(app):

    # -------- TABLE RENDER --------
    @app.callback(
        Output("users-table-container", "children"),
        Input("users-data", "data")
    )
    def render_table(users):
        if not users:
            return dbc.Alert("No users found", color="warning")

        rows = []
        for user in users:
            rows.append(html.Tr([
                html.Td(user["username"]),
                html.Td(user["full_name"]),
                html.Td(user["email"]),
                html.Td(dbc.Badge(user["role"], color="primary")),
                html.Td(dbc.Badge(
                    user["status"],
                    color="success" if user["status"] == "active" else "danger"
                )),
                html.Td([
                    dbc.Button("✏️", id={"type": "edit-user", "id": user["id"]}, size="sm", className="me-1"),
                    dbc.Button("🗑️", id={"type": "delete-user", "id": user["id"]}, size="sm", color="danger"),
                ])
            ]))

        return dbc.Table([
            html.Thead(html.Tr([
                html.Th("Username"),
                html.Th("Name"),
                html.Th("Email"),
                html.Th("Role"),
                html.Th("Status"),
                html.Th("Actions"),
            ])),
            html.Tbody(rows)
        ], bordered=True, hover=True, responsive=True)

    # -------- MODAL & CONTROLLER --------
    @app.callback(
        Output("users-data", "data"),
        Output("user-modal", "is_open"),
        Output("user-modal-title", "children"),
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
