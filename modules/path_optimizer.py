import os
import dash
from dash import html, dcc, Input, Output, State, callback_context
import pandas as pd
import dash_bootstrap_components as dbc
import heapq
from collections import defaultdict

DARK_BLUE = "#1a237e"
LIGHT_GREEN = "#4caf50"
ORANGE = "#ff9800"

PATH_DATA = "data/routes.csv"

def load_path_data():
    if os.path.exists(PATH_DATA):
        df = pd.read_csv(PATH_DATA)
        df["distance_m"] = pd.to_numeric(df["distance_m"], errors="coerce")
        df["accessible"] = df["accessible"].astype(str).str.lower() == "true"
        return df
    return pd.DataFrame(columns=["id", "start_location", "end_location", "distance_m", "accessible"])

def build_graph(df):
    graph = defaultdict(list)
    for _, row in df.iterrows():
        start = row["start_location"]
        end = row["end_location"]
        dist = row["distance_m"]
        accessible = row["accessible"]
        # Add both directions since routes are bidirectional
        graph[start].append((end, dist, accessible))
        graph[end].append((start, dist, accessible))
    return graph

def dijkstra_shortest_path(graph, start, end):
    if start not in graph or end not in graph:
        return None, float('inf'), []

    # Priority queue: (distance, node, path, accessibility_flags)
    pq = [(0, start, [start], [])]
    visited = set()
    min_dist = {node: float('inf') for node in graph}
    min_dist[start] = 0

    while pq:
        dist, current, path, access_flags = heapq.heappop(pq)

        if current in visited:
            continue
        visited.add(current)

        if current == end:
            return dist, path, access_flags

        for neighbor, edge_dist, accessible in graph[current]:
            if neighbor in visited:
                continue

            new_dist = dist + edge_dist
            if new_dist < min_dist[neighbor]:
                min_dist[neighbor] = new_dist
                new_path = path + [neighbor]
                new_flags = access_flags + [accessible]
                heapq.heappush(pq, (new_dist, neighbor, new_path, new_flags))

    return None, float('inf'), []

# ---------------- Layout ----------------
def layout():
    df = load_path_data()
    locations = sorted(set(df["start_location"].tolist() + df["end_location"].tolist())) if not df.empty else []

    return dbc.Container([
        html.H3("🗺️ Smart Route Finder", className="mb-4 text-info fw-bold"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-route me-2"),
                        "Find Your Path"
                    ], className="bg-primary text-white fw-bold"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label([
                                    html.I(className="fas fa-map-marker-alt me-2 text-success"),
                                    "From (Starting Point)"
                                ], className="form-label fw-semibold"),
                                dcc.Dropdown(
                                    id="origin-point",
                                    options=[{"label": f"📍 {loc}", "value": loc} for loc in locations],
                                    placeholder="🏫 Select departure location...",
                                    className="mb-3",
                                    style={"borderRadius": "8px", "color": "black"}
                                )
                            ], md=6),
                            dbc.Col([
                                html.Label([
                                    html.I(className="fas fa-flag-checkered me-2 text-danger"),
                                    "To (Destination)"
                                ], className="form-label fw-semibold"),
                                dcc.Dropdown(
                                    id="destination-point",
                                    options=[{"label": f"🎯 {loc}", "value": loc} for loc in locations],
                                    placeholder="🏁 Select arrival location...",
                                    className="mb-3",
                                    style={"borderRadius": "8px", "color": "black"}
                                )
                            ], md=6),
                        ], className="mb-4"),

                        dbc.Row([
                            dbc.Col([
                                dbc.Checkbox(
                                    id="accessibility-filter",
                                    label=[
                                        html.I(className="fas fa-wheelchair me-2"),
                                        "Wheelchair accessible routes only"
                                    ],
                                    className="mb-3"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Checkbox(
                                    id="show-alternatives",
                                    label=[
                                        html.I(className="fas fa-random me-2"),
                                        "Show alternative routes"
                                    ],
                                    className="mb-3"
                                )
                            ], md=6),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-search me-2"),
                                    "Find Best Route"
                                ], id="optimize-btn", color="success", size="lg", className="w-100 mb-2 py-3 fw-semibold"),
                            ], md=8),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-eraser me-2"),
                                    "Clear"
                                ], id="clear-btn", color="secondary", size="lg", className="w-100 mb-2 py-3"),
                            ], md=4),
                        ]),

                        dcc.Loading(
                            id="loading-route",
                            type="circle",
                            children=[html.Div(id="path-output")]
                        )
                    ])
                ], className="shadow-lg mb-4")
            ], md=8),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-info-circle me-2"),
                        "Route Tips"
                    ], className="bg-info text-white fw-bold"),
                    dbc.CardBody([
                        html.Ul([
                            html.Li([
                                html.I(className="fas fa-clock me-2 text-warning"),
                                "Average walking speed: 1.4 m/s"
                            ], className="mb-2"),
                            html.Li([
                                html.I(className="fas fa-wheelchair me-2 text-primary"),
                                "Accessible routes avoid stairs"
                            ], className="mb-2"),
                            html.Li([
                                html.I(className="fas fa-route me-2 text-success"),
                                "Shortest path calculated using Dijkstra's algorithm"
                            ], className="mb-2"),
                            html.Li([
                                html.I(className="fas fa-map me-2 text-info"),
                                "Campus covers multiple buildings and outdoor areas"
                            ], className="mb-0"),
                        ])
                    ])
                ], className="shadow mb-4"),

                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-star me-2"),
                        "Popular Routes"
                    ], className="bg-warning text-dark fw-bold"),
                    dbc.CardBody([
                        html.Div(id="popular-routes", children=[
                            html.P("📚 Library → Cafeteria", className="mb-1 text-muted"),
                            html.P("🏫 Main Gate → Admin Building", className="mb-1 text-muted"),
                            html.P("🏥 Medical Center → Parking", className="mb-0 text-muted"),
                        ])
                    ])
                ], className="shadow")
            ], md=4)
        ])
    ], fluid=True)

# ---------------- Path Optimization Callback ----------------
def register_find_routes_callbacks(app):
    @app.callback(
        [Output("path-output", "children"),
         Output("origin-point", "value"),
         Output("destination-point", "value"),
         Output("accessibility-filter", "value"),
         Output("show-alternatives", "value")],
        [Input("optimize-btn", "n_clicks"),
         Input("clear-btn", "n_clicks")],
        [State("origin-point", "value"),
         State("destination-point", "value"),
         State("accessibility-filter", "value"),
         State("show-alternatives", "value")],
        prevent_initial_call=True
    )
    def handle_route_actions(optimize_clicks, clear_clicks, origin, destination, accessibility_only, show_alternatives):
        ctx = callback_context
        if not ctx.triggered:
            return "", None, None, False, False

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Handle clear button
        if button_id == "clear-btn":
            return "", None, None, False, False

        # Handle optimize button
        if not origin or not destination:
            return dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "Please select both starting point and destination to find your route."
            ], color="warning", className="mt-3"), origin, destination, accessibility_only, show_alternatives

        if origin == destination:
            return dbc.Alert([
                html.I(className="fas fa-exclamation-circle me-2"),
                "Starting point and destination cannot be the same location."
            ], color="warning", className="mt-3"), origin, destination, accessibility_only, show_alternatives

        df = load_path_data()
        graph = build_graph(df)

        dist, path, access_flags = dijkstra_shortest_path(graph, origin, destination)

        if dist is None:
            return dbc.Alert([
                html.I(className="fas fa-times-circle me-2"),
                f"No route found between {origin} and {destination}. Please check if both locations exist."
            ], color="danger", className="mt-3"), origin, destination, accessibility_only, show_alternatives

        # Check accessibility if filter is enabled
        if accessibility_only and False in access_flags:
            return dbc.Alert([
                html.I(className="fas fa-wheelchair me-2"),
                "No fully accessible route found. Try disabling the accessibility filter or choose different locations."
            ], color="warning", className="mt-3"), origin, destination, accessibility_only, show_alternatives

        # Calculate estimated walking time (assuming 1.4 m/s average walking speed)
        walking_time_minutes = (dist / 1.4) / 60
        time_display = f"{walking_time_minutes:.1f} minutes" if walking_time_minutes < 60 else f"{walking_time_minutes/60:.1f} hours"

        path_str = " → ".join(path)
        access_status = "Fully Accessible" if all(access_flags) else "Partially Accessible"
        access_color = LIGHT_GREEN if all(access_flags) else ORANGE
        access_icon = "fas fa-wheelchair" if all(access_flags) else "fas fa-exclamation-triangle"

        result_card = dbc.Card([
            dbc.CardHeader([
                html.I(className="fas fa-check-circle me-2 text-success"),
                f"Route Found: {origin} to {destination}"
            ], className="bg-success text-white fw-bold"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6([
                            html.I(className="fas fa-route me-2"),
                            "Path Overview"
                        ], className="text-primary mb-2"),
                        html.P(path_str, className="fw-semibold fs-5 mb-3", style={"wordBreak": "break-word"})
                    ], md=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.I(className="fas fa-ruler me-2 text-info"),
                            html.Span(f"{dist:.0f} meters", className="fw-semibold")
                        ], className="mb-2")
                    ], md=4),
                    dbc.Col([
                        html.Div([
                            html.I(className="fas fa-clock me-2 text-warning"),
                            html.Span(f"~{time_display}", className="fw-semibold")
                        ], className="mb-2")
                    ], md=4),
                    dbc.Col([
                        html.Div([
                            html.I(className=f"{access_icon} me-2"),
                            html.Span(access_status, className="fw-semibold", style={"color": access_color})
                        ], className="mb-2")
                    ], md=4),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.I(className="fas fa-directions me-2 text-secondary"),
                            html.Span(f"{len(path)-1} segments", className="text-muted")
                        ])
                    ], md=12),
                ])
            ])
        ], className="mt-3 shadow-lg border-success")

        return result_card, origin, destination, accessibility_only, show_alternatives

