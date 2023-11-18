import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, dash_table
#from dash_table import DataTable
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from datetime import datetime, timedelta
import random

# Function to load data from CSV files
def load_data(plant, period, file_type):
    file_path = os.path.join(base_directory, plant, period, f'nazwa_{file_type}.csv')
    df = pd.read_csv(file_path)
    #print(df)
    return df

# Sample data generation
base_directory = 'sample_data'
available_plants = ['Plant1', 'Plant2', 'Plant3']
available_periods = ['Period1', 'Period2', 'Period3']

# Dash app initialization
app = dash.Dash(__name__)

# Define the title and subtitle
title = html.H1("Najwiekszy Polski Cracker", style={'textAlign': 'center'})
subtitle = html.H3("mISIe w formie", style={'textAlign': 'center'})

# App layout
app.layout = html.Div([
    title,
    subtitle,
    dcc.Tabs([
        dcc.Tab(label='Merged Tables', children=[
            html.Label("Select Plants:"),
            dcc.Dropdown(
                id='plant-dropdown',
                options=[{'label': plant, 'value': plant} for plant in available_plants],
                multi=True,
                value=[available_plants[0]]
            ),
    
            html.Label("Select Periods:"),
            dcc.RangeSlider(
                id='period-slider',
                min=0,
                max=len(available_periods) - 1,
                marks={i: period for i, period in enumerate(available_periods)},
                value=[0, len(available_periods) - 1]
            ),
    
            html.Button("Generate Merged Tables", id='generate-tables-button'),
    
            dcc.Tabs([
                dcc.Tab(label='Table Type 1', id='table-type1-tab'),
                dcc.Tab(label='Table Type 2', id='table-type2-tab'),
                dcc.Tab(label='Table Type 3', id='table-type3-tab')
            ]),
        ]),
    
        dcc.Tab(label='Compare Files', children=[
            html.Label("Select File 1:"),
            dcc.Dropdown(
                id='file1-dropdown',
                options=[{'label': plant, 'value': plant} for plant in available_plants],
                value=available_plants[0]
            ),
    
            html.Label("Select Period for File 1:"),
            dcc.RangeSlider(
                id='file1-period-slider',
                min=0,
                max=len(available_periods) - 1,
                marks={i: period for i, period in enumerate(available_periods)},
                value=[0, len(available_periods) - 1]
            ),
    
            html.Label("Select File Type for File 1:"),
            dcc.RadioItems(
                id='file1-type-radio',
                options=[
                    {'label': 'Type 1', 'value': 1},
                    {'label': 'Type 2', 'value': 2},
                    {'label': 'Type 3', 'value': 3}
                ],
                value=1,
                labelStyle={'display': 'block'}
            ),
    
            html.Label("Select File 2:"),
            dcc.Dropdown(
                id='file2-dropdown',
                options=[{'label': plant, 'value': plant} for plant in available_plants],
                value=available_plants[0]
            ),
    
            html.Label("Select Period for File 2:"),
            dcc.RangeSlider(
                id='file2-period-slider',
                min=0,
                max=len(available_periods) - 1,
                marks={i: period for i, period in enumerate(available_periods)},
                value=[0, len(available_periods) - 1]
            ),
    
            html.Label("Select File Type for File 2:"),
            dcc.RadioItems(
                id='file2-type-radio',
                options=[
                    {'label': 'Type 1', 'value': 1},
                    {'label': 'Type 2', 'value': 2},
                    {'label': 'Type 3', 'value': 3}
                ],
                value=1,
                labelStyle={'display': 'block'}
            ),
    
            html.Button("Compare Files", id='compare-files-button'),
    
            html.Div(id='comparison-output')
        ]),
    ])
])

@app.callback(
    [Output('table-type1-tab', 'children'),
     Output('table-type2-tab', 'children'),
     Output('table-type3-tab', 'children')],
    [Input('generate-tables-button', 'n_clicks')],
    [State('plant-dropdown', 'value'),
     State('period-slider', 'value')]
)
def generate_merged_tables(n_clicks, selected_plants, selected_periods):
    if n_clicks is None:
        raise PreventUpdate
    
    tables = []

    for file_type in range(1, 4):
        data = []
        for plant in selected_plants:
            plant_data = []
            for period_index in range(selected_periods[0], selected_periods[1] + 1):
                df = load_data(plant, available_periods[period_index], file_type)
                df['Plant'] = plant  # Add a column for plant name
                plant_data.append(df)
            
            # Concatenate data for the current plant and file type
            plant_data_concatenated = pd.concat(plant_data, axis=0, ignore_index=True)
            data.append(plant_data_concatenated)

        # Concatenate data for all selected plants and file type
        merged_df = pd.concat(data, axis=0)#, keys=[f'{plant}_{available_periods[i]}' for plant in selected_plants for i in range(selected_periods[0], selected_periods[1] + 1)])
        # print(merged_df.to_dict('records'))
        tables.append(html.Div([
            html.H4(f'Table Type {file_type}'),
            dash_table.DataTable(
                id=f'table-type{file_type}',
                columns=[{'name': col, 'id': col} for col in merged_df.columns],
                data=merged_df.to_dict('records'),
                sort_action='native',
                filter_action='native'
            )
        ]))

    return tables


# Callback for comparing files
@app.callback(
    Output('comparison-output', 'children'),
    [Input('compare-files-button', 'n_clicks')],
    [State('file1-dropdown', 'value'),
     State('file1-period-slider', 'value'),
     State('file1-type-radio', 'value'),
     State('file2-dropdown', 'value'),
     State('file2-period-slider', 'value'),
     State('file2-type-radio', 'value')]
)
def compare_files(n_clicks, file1_plant, file1_periods, file1_type, file2_plant, file2_periods, file2_type):
    if n_clicks is None:
        raise PreventUpdate

    file1_df = load_data(file1_plant, available_periods[file1_periods[0]], file1_type)
    file2_df = load_data(file2_plant, available_periods[file2_periods[0]], file2_type)

    # Perform any comparison or analysis as needed
    comparison_result = html.Div([
        html.H4('Comparison Result'),
        dcc.Markdown(f'''
            **File 1:** {file1_plant}, Period: {available_periods[file1_periods[0]]}, Type: {file1_type}
            
            **File 2:** {file2_plant}, Period: {available_periods[file2_periods[0]]}, Type: {file2_type}
            
            *Add your comparison or analysis here.*
        ''')
    ])

    return comparison_result

# Run the app
if __name__ == '__main__':
    
    app.run_server(debug=True)
