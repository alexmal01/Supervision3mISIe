import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, dash_table
#from dash_table import DataTable
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from datetime import datetime, timedelta
import random
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc

# Function to load data from CSV files
def load_data(plant, period, file_type):
    file_path = os.path.join(base_directory, plant, period, f'{file_type}.csv')
    df = pd.read_csv(file_path)
    #print(df)
    return df

base_directory = 'sample_data'
available_plants = ['Zaklad1', 'Zaklad2', 'Zaklad3']
available_periods = ['2020', '2021', '2022']

# Dash app initialization
app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])
load_figure_template('LUX')

# Define styles for the title and image container
title_style = {'textAlign': 'center', 'font-family': 'Monospace'}
container_style = {'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}

title = html.H1("N.P.C ", style=title_style)
image = html.Img(src=app.get_asset_url('images/logo.png'), style={'height': '5%', 'width': '5%'})
subtitle = html.Div(
    children=[
        html.H3("💥Największy ", style={'textAlign': 'center', 'font-family': 'Monospace', 'display': 'inline'}),
        html.H3("Polski", style={'color': 'red', 'display': 'inline'}),
        html.H3(" Cracker💥", style={'textAlign': 'center', 'font-family': 'Monospace', 'display': 'inline'})
    ],
    style={'textAlign': 'center'}
)

# App layout
app.layout = html.Div([
    html.Div([title, image], style=container_style),
    subtitle,
    dcc.Tabs([
        dcc.Tab(label='Przegląd SFCR', children=[
            html.Label("Wybierz zakłady:"),
            dcc.Dropdown(
                id='plant-dropdown',
                options=[{'label': plant, 'value': plant} for plant in available_plants],
                multi=True,
                value=[available_plants[0]]
            ),
    
            html.Label("Wybierz okres czasu:"),
            dcc.RangeSlider(
                id='period-slider',
                min=0,
                max=len(available_periods) - 1,
                marks={i: period for i, period in enumerate(available_periods)},
                value=[0, len(available_periods) - 1]
            ),
    
            html.Button("Pobierz dane", id='generate-tables-button'),
    
            dcc.Tabs([
                dcc.Tab(label='Dane jakościowe', id='table-type1-tab'),
                dcc.Tab(label='Tabele obligatoryjne', id='table-type2-tab'),
                dcc.Tab(label='Dane dla weryfikacji kompletności SFCR', id='table-type3-tab')
            ]),
        ]),
    
        dcc.Tab(label='Analiza SFCR', children=[
            html.Label("Wybierz zakłady:"),
            dcc.Dropdown(
                id='plant-analysis-dropdown',
                options=[{'label': plant, 'value': plant} for plant in available_plants],
                multi=False,
                value=[available_plants[0]]
            ),
    
            # html.Label("Wybierz okres czasu:"),
            # dcc.RangeSlider(
            #     id='file1-period-slider',
            #     min=0,
            #     max=len(available_periods) - 1,
            #     marks={i: period for i, period in enumerate(available_periods)},
            #     value=[0, len(available_periods) - 1]
            # ),
    
            # html.Label("Wybierz rodzaj pliku:"),
            # dcc.RadioItems(
            #     id='file1-type-radio',
            #     options=[
            #         {'label': 'Dane jakościowe', 'value': 'Struktura dla danych jakościowych'},
            #         {'label': 'Tabele obligatoryjne', 'value': 'Struktura dla tabel obligatoryjnych'},
            #         {'label': 'Dane dla weryfikacji kompletności SFCR', 'value': 'Struktura dla danych dla weryfikacji kompletności SFCR'}
            #     ],
            #     value=1,
            #     labelStyle={'display': 'block'}
            # ),
    
            html.Button("Analizuj", id='analyze-files-button'),
    
            html.Div(id='analyze-output')
        ]),

        dcc.Tab(label='Porównanie SFCR', children=[
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
    
            html.Label("Wybierz rodzaj pliku:"),
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
    
            html.Button("Porównaj", id='compare-files-button'),
    
            html.Div(id='comparison-output')
        ])
    ]),
    # add footer created by mISIe
    html.Div([
        html.Hr(),
        html.P('Created by mISIe🐻', style={'textAlign': 'center','font-family': 'Monospace', 'font-weight': 'bold'})
    ]),

],style={'margin': '20px'})

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
    file_types = ['Struktura dla danych jakościowych', 'Struktura dla obligatoryjnych tabel', 'Struktura dla danych dla weryfikacji kompletności SFCR']
    
    for file_type in file_types:
        data = []
        for plant in selected_plants:
            plant_data = []
            for period_index in range(selected_periods[0], selected_periods[1] + 1):
                # check if path exists
                if os.path.exists(os.path.join(base_directory, plant, available_periods[period_index], f'{file_type}.csv')):
                    df = load_data(plant, available_periods[period_index], file_type)
                    df['Zaklad'] = plant  # Add a column for plant name
                    plant_data.append(df)
            
            # Concatenate data for the current plant and file type
            plant_data_concatenated = pd.concat(plant_data, axis=0, ignore_index=True)
            data.append(plant_data_concatenated)

        # Concatenate data for all selected plants and file type
        merged_df = pd.concat(data, axis=0)#, keys=[f'{plant}_{available_periods[i]}' for plant in selected_plants for i in range(selected_periods[0], selected_periods[1] + 1)])
        # print(merged_df.to_dict('records'))
        tables.append(html.Div([
            #html.H4(f'{file_type}'),
            dash_table.DataTable(
                id=f'table-type{file_type}',
                columns=[{'name': col, 'id': col} for col in merged_df.columns],
                data=merged_df.to_dict('records'),
                sort_action='native',
                filter_action='native'
            )
        ]))

    return tables

# Callback for SFCR analysis
@app.callback(
    Output('analyze-output', 'children'),
    [Input('analyze-files-button', 'n_clicks')],
    [State('plant-analysis-dropdown', 'value')]
)
def analyze_files(n_clicks, selected_plant):
    if n_clicks is None:
        raise PreventUpdate

    # Get time periods for the selected plant
    periods = []
    for period in available_periods:
        if os.path.exists(os.path.join(base_directory, selected_plant, period)):
            periods.append(period)

    # Get file types for the selected plant
    file_types = []
    for file_type in ['Struktura dla danych jakościowych', 'Struktura dla obligatoryjnych tabel', 'Struktura dla danych dla weryfikacji kompletności SFCR']:
        if os.path.exists(os.path.join(base_directory, selected_plant, periods[0], f'{file_type}.csv')):
            file_types.append(file_type)
    
    # Load data for the selected plant, period and file type
    # data = []
    # for file_type in file_types:
    #     file_type_data = []
    #     for period in periods:
    #         df = load_data(selected_plant, period, file_type)
    #         file_type_data.append(df)
        
    #     # Concatenate data for the current file type
    #     file_type_data_concatenated = pd.concat(file_type_data, axis=0, ignore_index=True)
    #     data.append(file_type_data_concatenated)
    
    statistics = pd.DataFrame(columns=periods, index=['Sekcja', 'Tabele', 'Słowa kluczowe'])

    for period in periods:
        df1 = load_data(selected_plant, period, 'Struktura dla danych jakościowych')
        df2 = load_data(selected_plant, period, 'Struktura dla obligatoryjnych tabel')
        random_num = df2['ID_TAB'].iloc[0]
        # Set WARTOŚĆ to null where ID_TAB is equal to random_num
        df2.loc[df2['ID_TAB'] == random_num, 'WARTOŚĆ'] = None
        df3 = load_data(selected_plant, period, 'Struktura dla danych dla weryfikacji kompletności SFCR')
        #Calculate % of missing sections (37 is the number of sections in the SFCR)
        missing_sections_frac = 1 -round(len(df1['ID_SEKCJA'].unique())/37,2)
        # Search tabele obligatoryjne for grouped ID_TAB and count if WARTOŚĆ is all null
        df2_grouped = df2.groupby('ID_TAB').count()
        df2_grouped = df2_grouped[df2_grouped['WARTOŚĆ'] == 0]
        df2_grouped = df2_grouped.reset_index()
        number_of_not_present_tables = len(df2_grouped['ID_TAB'].tolist())
        number_of_present_tables_frac = 1 -round(number_of_not_present_tables/len(df2['ID_TAB'].unique()))
        # Search in which sections there are missing key words
        num_ans = len(df3['ID_PYTANIA'].unique())
        num_is_key_word = len(df3[df3['CZY WYSTĄPIŁ KLUCZ (0/1)'] == 1]['ID_PYTANIA'].unique())
        missing_keywords_frac = 1 - round((num_ans - num_is_key_word)/num_ans,2)
        statistics[period] = [missing_sections_frac, number_of_present_tables_frac, missing_keywords_frac]

    # Add row and column summaries
    statistics.loc['Kompletność'] = statistics.mean(axis=0)
    statistics['Średnia'] = statistics.mean(axis=1)
    statistics = statistics.round(2)
    statistics = statistics.reset_index().rename(columns={'index': 'Procent kompletności'})
    # Perform any analysis as needed
    analysis_result = html.Div([
        dash_table.DataTable(
            id='table-type1',
            columns=[{'name': col, 'id': col} for col in statistics.columns],
            data=statistics.reset_index().to_dict('records'),
            # Outline last row and column
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                },
                {
                    'if': {'row_index': 3},
                    'border': '1px solid black',
                    'fontWeight': 'bold',
                    'backgroundColor': 'rgb(140, 211, 255)'
                }
            ],
            style_cell={
                'textAlign': 'center',
                'font-family': 'sans-serif',
                'font-size': '1.2rem'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_table={
                'overflowX': 'auto',
                'width': '100%'
            }
        ),
        
    ])

    return analysis_result


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
