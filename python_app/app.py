import os
import pathlib
from datetime import datetime

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
import plotly.graph_objs as go
import dash_daq as daq

import pandas as pd

import asyncio
import threading
import IN100_ble
from time import sleep

## --Config--
DEVICE_NAME = "IN100"

#--------------------------------------------------------------------
# Running the server and BLE
#--------------------------------------------------------------------

def run_server():
    app.run_server(debug=True, port=8050, use_reloader=False)

def start_BLE(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(IN100_ble.IN100_connect(DEVICE_NAME))

device_address = ""

if __name__ == "__main__":

    ble_loop = asyncio.new_event_loop()
    ble_thread = threading.Thread(target=start_BLE, args=(ble_loop,), daemon=True)
    ble_thread.start()

    dash_thread = threading.Thread(target=run_server, daemon=True)
    
    # Wait for the BLE connection to initialize
    APP_PATH = str(pathlib.Path(__file__).parent.resolve())
    date = datetime.date(datetime.today())
    while not os.path.exists(os.path.join(APP_PATH, os.path.join("data", f"ble_data_{date}.csv"))):
        print("Waiting for CSV to be created...")
        sleep(1)

    # MAIN PROGRAM CONTINUES NEAR THE END OF THE FILE

#---------------Other stuff------------------------------------

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "IN100 BLE Beacon Data"
server = app.server
app.config["suppress_callback_exceptions"] = True

def read_data(date = datetime.date(datetime.today())) :
    APP_PATH = str(pathlib.Path(__file__).parent.resolve())
    df = pd.read_csv(os.path.join(APP_PATH, os.path.join("data", f"ble_data_{date}.csv")), skipinitialspace=True)
    return df

df = read_data()
params = list(df)
max_length = len(df)

suffix_row = "_row"
suffix_button_id = "_button"
suffix_sparkline_graph = "_sparkline_graph"
suffix_count = "_count"

# Different tabs for Dashboard / Settings
def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Settings-tab",
                        label="Settings",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Dashboard-tab",
                        label="Dashboard",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )

# Initial data handling
def init_df():
    ret = {}
    for col in list(df[1:]):
        data = df[col]
        stats = data.describe()

        std = stats["std"].tolist()

        ret.update(
            {
                col: {
                    "count": stats["count"].tolist(),
                    "data": data,
                    "mean": stats["mean"].tolist(),
                    "std": std,
                    "min": stats["min"].tolist(),
                    "max": stats["max"].tolist()
                }
            }
        )

    return ret

# Initial data (execution)
state_dict = init_df()


def init_value_setter_store():
    # Initialize store data
    state_dict = init_df()
    return state_dict


# Settings tab
def build_tab_1():
    return [
        # Manually select metrics
        html.Div(
            id="set-specs-intro-container",
            # className='twelve columns',
            children=html.P(
                "Use historical control limits to establish a benchmark, or set new values."
            ),
        ),
        html.Div(
            id="settings-menu",
            children=[
                html.Div(
                    id="metric-select-menu",
                    # className='five columns',
                    children=[
                        html.Label(id="metric-select-title", children="Select Metrics"),
                        html.Br(),
                        dcc.Dropdown(
                            id="metric-select-dropdown",
                            options=list(
                                {"label": param, "value": param} for param in params[1:]
                            ),
                            value=params[1],
                        ),
                    ],
                ),
                html.Div(
                    id="value-setter-menu",
                    # className='six columns',
                    children=[
                        html.Div(id="value-setter-panel"),
                        html.Br(),
                        html.Div(
                            id="button-div",
                            children=[
                                html.Button("Update", id="value-setter-set-btn"),
                                html.Button(
                                    "View current setup",
                                    id="value-setter-view-btn",
                                    n_clicks=0,
                                ),
                            ],
                        ),
                        html.Div(
                            id="value-setter-view-output", className="output-datatable"
                        ),
                    ],
                ),
            ],
        ),
    ]

# Left side of the data page
def build_quick_stats_panel():

    last_timestamp = datetime.fromtimestamp(state_dict["timestamp"]["data"].tolist()[-1])

    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                children=[
                    html.P("Device info"),
                    html.Table(
                        [
                            html.Tr([html.Td("Name"), html.Td("IN100")]),
                            html.Tr([html.Td("Address"), html.Td(device_address)]),
                            html.Tr([html.Td("Last received"), html.Td(str(datetime.date(last_timestamp)) + " " + str(datetime.time(last_timestamp)))])
                        ], 
                        id="device-info-table"
                    ), # TODO : configurable name / address, get real data
                ],
            ),
            html.Div(
                id="card-2",
                children=[
                    html.P("Vcc"),
                    daq.Gauge(
                        id="vcc-gauge",
                        max=3.0,
                        min=0,
                        showCurrentValue=True,  # default size 200 pixel
                    ),
                ],
            ),
            html.Div(
                id="utility-card",
                children=[daq.StopButton(id="stop-button", size=160, n_clicks=0)],
            ),
        ],
    )


def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)

def build_top_panel(stop_interval):
    return html.Div(
        id="top-section-container",
        className="row",
        children=[
            # Metrics summary
            html.Div(
                id="metric-summary-session",
                className="eight columns",
                children=[
                    generate_section_banner("Metrics Summary"),
                    html.Div(
                        id="metric-div",
                        children=[
                            generate_metric_list_header(),
                            html.Div(
                                id="metric-rows",
                                children=[
                                    generate_metric_row_helper(stop_interval, 1),
                                    generate_metric_row_helper(stop_interval, 2),
                                    generate_metric_row_helper(stop_interval, 3),
                                    generate_metric_row_helper(stop_interval, 4),
                                    generate_metric_row_helper(stop_interval, 5),
                                    generate_metric_row_helper(stop_interval, 6),
                                ],
                            ),
                        ],
                    ),
                ],
            )
        ],
    )

# Build header for Metrics summary
def generate_metric_list_header():
    return generate_metric_row(
        "metric_header",
        {"height": "3rem", "margin": "1rem 0", "textAlign": "center"},
        {"id": "m_header_1", "children": html.Div("Parameter")},
        {"id": "m_header_2", "children": html.Div("Count")},
        {"id": "m_header_3", "children": html.Div("Sparkline")}
    )


def generate_metric_row_helper(stop_interval, index):
    item = params[index]

    div_id = item + suffix_row
    button_id = item + suffix_button_id
    sparkline_graph_id = item + suffix_sparkline_graph
    count_id = item + suffix_count

    return generate_metric_row(
        div_id,
        None,
        {
            "id": item,
            "className": "metric-row-button-text",
            "children": html.Button(
                id=button_id,
                className="metric-row-button",
                children=item,
                title="Click to visualize live SPC chart",
                n_clicks=0,
            ),
        },
        {"id": count_id, "children": "0"},
        {
            "id": item + "_sparkline",
            "children": dcc.Graph(
                id=sparkline_graph_id,
                style={"width": "100%", "height": "95%"},
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": state_dict["timestamp"]["data"].tolist()[:stop_interval],
                                "y": state_dict[item]["data"][:stop_interval],
                                "mode": "lines",
                                "name": item,
                                "line": {"color": "#f4d44d"},
                            }
                        ],
                        "layout": {
                            "uirevision": True,
                            "margin": dict(l=0, r=0, t=4, b=4, pad=0),
                            "xaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "yaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                        },
                    }
                ),
            ),
        },
    )


def generate_metric_row(id, style, col1, col2, col3):
    if style is None:
        style = {"height": "8rem", "width": "100%"}

    return html.Div(
        id=id,
        className="row metric-row",
        style=style,
        children=[
            html.Div(
                id=col1["id"],
                className="one column",
                style={"margin-right": "2.5rem", "minWidth": "50px"},
                children=col1["children"],
            ),
            html.Div(
                id=col2["id"],
                style={"textAlign": "center"},
                className="one column",
                children=col2["children"],
            ),
            html.Div(
                id=col3["id"],
                style={"height": "100%"},
                className="four columns",
                children=col3["children"],
            ),
        ],
    )

#---------------------------Graph panel---------------------------------

def build_chart_panel():
    return html.Div(
        id="control-chart-container",
        className="twelve columns",
        children=[
            generate_section_banner("Graph"),
            dcc.Graph(
                id="control-chart-live",
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": [],
                                "y": [],
                                "mode": "lines+markers",
                                "name": params[2],
                            }
                        ],
                        "layout": {
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                            "xaxis": dict(
                                showline=False, showgrid=False, zeroline=False
                            ),
                            "yaxis": dict(
                                showgrid=False, showline=False, zeroline=False
                            ),
                            "autosize": True,
                        },
                    }
                ),
            ),
        ],
    )

 # TODO : configurable graph to show either Vcc or acc
def generate_graph(interval, specs_dict, col):
    stats = state_dict[col]
    col_data = stats["data"].tolist()
    if (col == 1) :
        max_accepted_value = 3.0 
        min_accepted_value = 1.1
    else : 
        max_accepted_value = max(col_data) + 1
        min_accepted_value = min(col_data) - 1

    # Get timestamps
    timestamps = [datetime.fromtimestamp(t) for t in state_dict["timestamp"]["data"].tolist()]

    x_array = timestamps
    y_array = col_data

    # red points on values outside expected range
    unexpected_values_trace = {
        "x": [],
        "y": [],
        "name": "Out of Control",
        "mode": "markers",
        "marker": dict(color="rgba(210, 77, 87, 0.7)", symbol="square", size=11),
    }

    for index, data in enumerate(y_array):
        if data >= max_accepted_value or data <= min_accepted_value:
            unexpected_values_trace["x"].append(index + 1)
            unexpected_values_trace["y"].append(data)

    fig = {
        "data": [
            {
                "x": x_array,
                "y": y_array,
                "mode": "lines+markers",
                "name": col,
                "line": {"color": "#f4d44d"},
            },
            unexpected_values_trace,
        ]
    }

    fig["layout"] = dict(
        margin=dict(t=40),
        hovermode="closest",
        uirevision=col,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={"font": {"color": "darkgray"}, "orientation": "h", "x": 0, "y": 1.1},
        font={"color": "darkgray"},
        showlegend=True,
        xaxis={
            "anchor": "free",
            "zeroline": False,
            "showgrid": False,
            "title": "Time",
            "showline": False,
            "autorange": True,
            "titlefont": {"color": "darkgray"},
        },
        yaxis={
            "title": col,
            "showgrid": False,
            "showline": False,
            "zeroline": False,
            "autorange": True,
            "titlefont": {"color": "darkgray"},
        },
        xaxis2={
            "anchor": "free",
            "title": "Count",
            "autorange": True,
            "titlefont": {"color": "darkgray"},
            "showgrid": False,
        },
        yaxis2={
            "anchor": "free",
            "overlaying": "y",
            "side": "right",
            "showticklabels": False,
            "titlefont": {"color": "darkgray"},
        },
    )

    return fig

#-----------------------------------Metrics summary panel-----------------------

def update_sparkline(interval, param):
    x_array = state_dict["timestamp"]["data"].tolist()
    y_array = state_dict[param]["data"].tolist()

    if interval == 0:
        x_new = y_new = None

    else:
        x_new = x_array[:][-1]
        y_new = y_array[:][-1]

    return dict(x=[[x_new]], y=[[y_new]]), [0]


def update_count(interval, col, data):
    if interval == 0:
        return "0"

    total_count = len(state_dict[col]["data"].tolist())

    return str(total_count + 1)

#---------------------------------App layout and callbacks-----------------------------

app.layout = html.Div(
    id="big-app-container",
    children=[
        dcc.Interval(
            id="interval-component",
            interval=5000,  # in milliseconds
            n_intervals=len(state_dict["timestamp"]["data"].tolist()),
            disabled=True,
        ),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
        dcc.Store(id="value-setter-store", data=init_value_setter_store()),
        dcc.Store(id="n-interval-stage", data=len(state_dict["timestamp"]["data"].tolist()))
    ],
)

# handle switching between tabs / top level
@app.callback(
    [Output("app-content", "children"), Output("interval-component", "n_intervals")],
    [Input("app-tabs", "value")],
    [State("n-interval-stage", "data")],
)
def render_tab_content(tab_switch, stop_interval):
    if tab_switch == "tab1":
        return build_tab_1(), stop_interval
    return (
        html.Div(
            id="status-container",
            children=[
                build_quick_stats_panel(),
                html.Div(
                    id="graphs-container",
                    children=[build_top_panel(stop_interval), build_chart_panel()],
                ),
            ],
        ),
        stop_interval,
    )


# Callbacks for stopping interval update
@app.callback(
    [Output("interval-component", "disabled"), Output("stop-button", "buttonText")],
    [Input("stop-button", "n_clicks")],
    [State("interval-component", "disabled")],
)
def stop_production(n_clicks, current):
    if n_clicks == 0:
        return True, "start"
    return not current, "stop" if current else "start"


# ======= update progress gauge =========
@app.callback(
    output=[Output("vcc-gauge", "value"), Output("vcc-gauge", "color")],
    inputs=[Input("interval-component", "n_intervals")],
)
def update_gauge(interval):
    x_array = state_dict["vcc_V"]["data"].tolist()
    if x_array:
        val = x_array[-1]
        if val > 2 : 
            color = "green"
        elif val > 1.2 :
            color = "yellow"
        else : 
            color = "red"

        return val, color  # Return the last value

    return 0, "red"  # Default value if state_dict is missing or empty

# Callback to reload the CSV file dynamically and all shown data
@app.callback(
    Output("value-setter-store", "data"),
    Output("device-info-table", "children"),
    Output("n-interval-stage", "data"),
    Input("interval-component", "n_intervals"),
    prevent_initial_call=True
)
def update_tables(n_intervals):
    global df, params, max_length, state_dict
    print("Updating DB")

    df = read_data()
    params = list(df)
    max_length = len(df)
    state_dict = init_df()

    last_timestamp = datetime.fromtimestamp(int(state_dict["timestamp"]["data"].tolist()[-1]))
    n_interval_stage_value = len(state_dict["timestamp"]["data"].tolist())

    new_table = [
        html.Tr([html.Td("Name"), html.Td("IN100")]),
        html.Tr([html.Td("Address"), html.Td(device_address)]),
        html.Tr([html.Td("Last received"), html.Td(str(datetime.date(last_timestamp)) + " " + str(datetime.time(last_timestamp)))]),
    ]

    return init_value_setter_store(), new_table, n_interval_stage_value

# decorator for list of output
def create_callback(param):
    def callback(interval, stored_data):
        count = update_count(
            interval, param, stored_data
        )
        spark_line_data = update_sparkline(interval, param)
        return count, spark_line_data   

    return callback


for param in params[1:]:
    update_param_row_function = create_callback(param)
    app.callback(
        output=[
            Output(param + suffix_count, "children"),
            Output(param + suffix_sparkline_graph, "extendData"),
        ],
        inputs=[Input("interval-component", "n_intervals")],
        state=[State("value-setter-store", "data")],
    )(update_param_row_function)


#  ======= button to choose/update figure based on click ============
@app.callback(
    output=Output("control-chart-live", "figure"),
    inputs=[
        Input("interval-component", "n_intervals"),
        Input(params[1] + suffix_button_id, "n_clicks"),
        Input(params[2] + suffix_button_id, "n_clicks"),
        Input(params[3] + suffix_button_id, "n_clicks"),
        Input(params[4] + suffix_button_id, "n_clicks"),
        Input(params[5] + suffix_button_id, "n_clicks"),
    ],
    state=[State("value-setter-store", "data"), State("control-chart-live", "figure")],
)
def update_control_chart(interval, n1, n2, n3, n4, n5, data, cur_fig):
    # Find which one has been triggered
    ctx = dash.callback_context

    if not ctx.triggered:
        return generate_graph(interval, data, params[1])

    if ctx.triggered:
        # Get most recently triggered id and prop_type
        splitted = ctx.triggered[0]["prop_id"].split(".")
        prop_id = splitted[0]
        prop_type = splitted[1]

        if prop_type == "n_clicks":
            curr_id = cur_fig["data"][0]["name"]
            prop_id = prop_id[:-7]
            if curr_id == prop_id:
                return generate_graph(interval, data, curr_id)
            else:
                return generate_graph(interval, data, prop_id)

        if prop_type == "n_intervals" and cur_fig is not None:
            curr_id = cur_fig["data"][0]["name"]
            return generate_graph(interval, data, curr_id)

#--------------------------------------------------------------------
# Main program part 2
#--------------------------------------------------------------------

if __name__ == "__main__":
    dash_thread.start()

    # Keep the main thread alive
    ble_thread.join()
    dash_thread.join()