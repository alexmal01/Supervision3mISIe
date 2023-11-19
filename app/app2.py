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
    
            html.Label("Wybierz okres:"),
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
            html.Label("Wybierz zakład 1:"),
            dcc.Dropdown(
                id='file1-dropdown',
                options=[{'label': plant, 'value': plant} for plant in available_plants],
                value=available_plants[0]
            ),
    
            html.Label("Wybierz okres dla zakładu 1:"),
            dcc.Dropdown(
                id='file1-period-dropdown',
                options=[{'label': period, 'value': period} for period in available_periods],
                value=available_periods[0]
            ),
    
            html.Label("Wybierz Zakład 2:"),
            dcc.Dropdown(
                id='file2-dropdown',
                options=[{'label': plant, 'value': plant} for plant in available_plants],
                value=available_plants[0]
            ),
    
            html.Label("Wybierz okres dla zakładu 2:"),
            dcc.Dropdown(
                id='file2-period-dropdown',
                options=[{'label': period, 'value': period} for period in available_periods],
                value=available_periods[0]
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
        df2_grouped = df2.groupby('FORMULARZ').count()
        df2_grouped = df2_grouped[df2_grouped['WARTOŚĆ'] == 0]
        df2_grouped = df2_grouped.reset_index()
        number_of_not_present_tables = len(df2_grouped['FORMULARZ'].tolist())
        number_of_present_tables_frac = 1 -round(number_of_not_present_tables/len(df2['FORMULARZ'].unique()))
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
        dcc.Markdown(f'''
            **Liczba zgromadzonych SFCR:** {len(periods)}
        ''')
        
    ])

    return analysis_result


# Callback for comparing files
@app.callback(
    Output('comparison-output', 'children'),
    [Input('compare-files-button', 'n_clicks')],
    [State('file1-dropdown', 'value'),
     State('file1-period-dropdown', 'value'),
     State('file2-dropdown', 'value'),
     State('file2-period-dropdown', 'value')]
)
def compare_files(n_clicks, file1_plant, file1_period, file2_plant, file2_period):
    if n_clicks is None:
        raise PreventUpdate

    # Check if the selected SFCR files exist
    if not os.path.exists(os.path.join(base_directory, file1_plant, file1_period, 'Struktura dla danych jakościowych.csv')):
        return html.Div([  
            dcc.Markdown(f'''
                **UWAGA:** Nie znalezniono plików SFCR dla zakłdu: {file1_plant} oraz okresu: {file1_period}!
            ''')
        ])
    elif not os.path.exists(os.path.join(base_directory, file2_plant, file2_period, 'Struktura dla danych jakościowych.csv')):
        return html.Div([
            dcc.Markdown(f'''
                **UWAGA:** Nie znalezniono plików SFCR dla zakłdu: {file2_plant} oraz okresu: {file2_period}!
            ''')
        ])

    tables1_df = load_data(file1_plant, file1_period, 'Struktura dla obligatoryjnych tabel')
    tables2_df = load_data(file2_plant, file2_period, 'Struktura dla obligatoryjnych tabel')
    keywords1_df = load_data(file1_plant, file1_period, 'Struktura dla danych dla weryfikacji kompletności SFCR')
    keywords2_df = load_data(file2_plant, file2_period, 'Struktura dla danych dla weryfikacji kompletności SFCR')

    # Merge tables on FORMULARZ, WIERSZ, KOLUMNA and calculate the difference between WARTOŚĆ_x and WARTOŚĆ_y, then sort by the difference in descending order considering absolute values
    merged_df = pd.merge(tables1_df, tables2_df, on=['FORMULARZ', 'WIERSZ', 'KOLUMNA'], suffixes=('_x', '_y'))
    merged_df['RÓŻNICA'] = merged_df['WARTOŚĆ_x'] - merged_df['WARTOŚĆ_y']
    merged_df = merged_df.sort_values(by=['RÓŻNICA'], ascending=False).reset_index(drop=True)
    # Select FORMULARZ, WIERSZ, KOLUMNA, RÓŻNICA columns
    merged_df = merged_df[['FORMULARZ', 'WIERSZ', 'KOLUMNA', 'RÓŻNICA']]
    #print(merged_df)
    # Merge keywords on ID_PYTANIA and calculate the difference between CZY WYSTĄPIŁ KLUCZ (0/1)_x and CZY WYSTĄPIŁ KLUCZ (0/1)_y, then sort by the difference in descending order considering absolute values
    keywords_merged_df = pd.merge(keywords1_df, keywords2_df, on=['ID_PYTANIA'], suffixes=('_x', '_y'))
    keywords_merged_df['RÓŻNICA'] = keywords_merged_df['CZY WYSTĄPIŁ KLUCZ (0/1)_x'] - keywords_merged_df['CZY WYSTĄPIŁ KLUCZ (0/1)_y']
    keywords_merged_df = keywords_merged_df.sort_values(by=['RÓŻNICA'], ascending=False).reset_index(drop=True)
    # Select ID_PYTANIA, RÓŻNICA columns
    keywords_merged_df = keywords_merged_df[['ID_PYTANIA', 'RÓŻNICA']]
    num_ans = len(keywords_merged_df['ID_PYTANIA'].unique())
    # Calculate indicator of similarity in keywords (near 1 indicates that Zaklad1 has perfect and Zaklad2 has no keywords, near -1 indicates that Zaklad2 has perfect and Zaklad1 has no keywords and 0 indicates that both Zaklads have the same strength in terms of keywords)
    similarity_indicator = round((keywords_merged_df['RÓŻNICA'].sum()/num_ans),2)
    #print(keywords_merged_df)

    # Display the results

    # Perform any comparison or analysis as needed
    comparison_result = html.Div([
        # Wrap both DataTables in a single div
        html.Div([
            # First DataTable
            html.Div([
                html.Label("Różnica w tabelach", style={'textAlign': 'center'}),
                dash_table.DataTable(
                id='table-type1',
                columns=[{'name': col, 'id': col} for col in merged_df.columns],
                data=merged_df.round(2).to_dict('records'),
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
                    #'width': '45%',  # Adjust as needed
                    'display': 'inline-block',
                    'verticalAlign': 'top',
                    #'margin': '0 25%'
                },
                page_action='native',
                page_current=0,
                page_size=10,
            )], style={'width': '45%',  'display': 'inline-block'}),

            # Second DataTable
            html.Div([
                html.Label("Różnica flag słów kluczowych", style={'textAlign': 'center'}),
                dash_table.DataTable(
                id='table-type2',
                columns=[{'name': col, 'id': col} for col in keywords_merged_df.columns],
                data=keywords_merged_df.to_dict('records'),
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
                    #'width': '45%',  # Adjust as needed
                    'display': 'inline-block',
                    'verticalAlign': 'top',
                    #'margin': '0 75%'
                },
                page_action='native',
                page_current=0,
                page_size=10,
            )], style={'width': '45%',  'display': 'inline-block', 'margin': '0 5%'}),
        ]),

        dcc.Markdown(f'''
            **Podobieństwo w słowach kluczowych:** {similarity_indicator}
            Wskaźnik podobieństwa w słowach kluczowych wskazuje na to, jak bardzo słowa kluczowe w SFCR dla zakładu 1 są podobne do słów kluczowych w SFCR dla zakładu 2. Wskaźnik ten jest obliczany jako suma różnic w słowach kluczowych podzielona przez liczbę pytań w SFCR.
            Im bliżej 1 tym lepiej dla zakładu 1, im bliżej -1 tym lepiej dla zakładu 2, a im bliżej 0 tym lepiej bardziej podobne są dokumenty wybranych zakładów w kontekście słów kluczowych.
        ''')

    ])


    return comparison_result

# Run the app
if __name__ == '__main__':
    
    app.run_server(debug=True)
