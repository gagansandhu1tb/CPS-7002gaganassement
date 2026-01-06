from dash import html
import dash_bootstrap_components as dbc

def navigation_panel(user):
    user_privilege = user.get('role', 'student') if user else 'student'
    
    # Core navigation items for all users
    core_items = [
        dbc.Button(
            "Dashboard",
            id="btn-dashboard",
            color="dark",
            className="w-100 mb-3",
            style={"textAlign": "left", "borderRadius": "0"}
        ),
        dbc.Button("Find Routes", id="btn-find-routes", color="dark", className="w-100 mb-3", style={"textAlign": "left", "borderRadius": "0"}),
        dbc.Button("Notifications", id="btn-notifications", color="dark", className="w-100 mb-3", style={"textAlign": "left", "borderRadius": "0"}),
    ]
    
    # Administrative controls - restricted access
    admin_controls = [
        dbc.Button(
            "Users",
            id="btn-users", 
            color="secondary" if user_privilege == 'admin' else "dark",
            className="w-100 mb-3",
            style={"textAlign": "left", "borderRadius": "0"},
            disabled=(user_privilege != 'admin')
        ),
        dbc.Button(
            "Locations", 
            id="btn-locations", 
            color="secondary" if user_privilege == 'admin' else "dark",
            className="w-100 mb-3", 
            style={"textAlign": "left", "borderRadius": "0"},
            disabled=(user_privilege != 'admin')
        ),
        dbc.Button(
            "Routes", 
            id="btn-routes", 
            color="secondary" if user_privilege == 'admin' else "dark",
            className="w-100 mb-3", 
            style={"textAlign": "left", "borderRadius": "0"},
            disabled=(user_privilege != 'admin')
        ),
        dbc.Button(
            "Reports", 
            id="btn-reports", 
            color="secondary" if user_privilege == 'admin' else "dark",
            className="w-100 mb-3", 
            style={"textAlign": "left", "borderRadius": "0"},
            disabled=(user_privilege != 'admin')
        ),
    ]
    
    core_items.extend(admin_controls)
    
    # Add logout button at the bottom
    core_items.append(
        dbc.Button(
            "Logout",
            id="logout-btn",
            color="danger",
            className="w-100 mt-4",
            style={"textAlign": "left", "borderRadius": "0"}
        )
    )
    
    return html.Div([
        html.H4("Menu", className="text-light mb-4"),
        html.Div(core_items)
    ], style={
        "background": "linear-gradient(180deg, #2c3e50 0%, #34495e 100%)",
        "padding": "20px",
        "height": "100vh",
        "borderRadius": "0"
    })

def dashboard_layout(user, content=None):
    if content is None:
        # Create a more informative dashboard
        user_role = user.get('role', 'user')
        
        # Quick stats cards
        stats_cards = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-tachometer-alt fa-2x text-primary mb-2"),
                            html.H5("Dashboard", className="text-primary mb-0 fw-bold"),
                            html.Small("System Overview", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="bg-light border-0 shadow-sm")
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-user fa-2x text-success mb-2"),
                            html.H5(user.get('username', 'User'), className="text-success mb-0 fw-bold"),
                            html.Small(f"Role: {user_role.title()}", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="bg-light border-0 shadow-sm")
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-clock fa-2x text-info mb-2"),
                            html.H5("Active", className="text-info mb-0 fw-bold"),
                            html.Small("Session Status", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="bg-light border-0 shadow-sm")
            ], width=4),
        ], className="mb-4")
        
        # Quick actions
        quick_actions = dbc.Card([
            dbc.CardHeader([
                html.I(className="fas fa-bolt me-2 text-warning"),
                html.Span("Quick Actions", className="fw-bold")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-route me-2"),
                            "Find Routes"
                        ], id="btn-find-routes", color="primary", className="w-100 mb-2", 
                        style={"textAlign": "left"})
                    ], md=6),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-bell me-2"),
                            "Notifications"
                        ], id="btn-notifications", color="info", className="w-100 mb-2",
                        style={"textAlign": "left"})
                    ], md=6),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-users me-2"),
                            "Users"
                        ], id="btn-users", color="success", className="w-100 mb-2",
                        style={"textAlign": "left"}, 
                        disabled=(user_role != 'admin'))
                    ], md=6),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-map-marker-alt me-2"),
                            "Locations"
                        ], id="btn-locations", color="warning", className="w-100 mb-2",
                        style={"textAlign": "left"},
                        disabled=(user_role != 'admin'))
                    ], md=6),
                ])
            ])
        ], className="shadow-sm")
        
        content = html.Div([
            html.H4("System Dashboard", className="mb-4 fw-bold text-dark"),
            stats_cards,
            quick_actions
        ])
    
    return dbc.Container([
        dbc.Row([
            dbc.Col(navigation_panel(user), width=2),
            dbc.Col(
                html.Div(content, style={"padding": "20px"}), 
                width=10
            )
        ])
    ], fluid=True)

# No callbacks - all in app.py
def dashboard_callbacks(app):
    pass