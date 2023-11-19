import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import os
import pandas as pd

# Przykładowe dane
# Zakłady dostępne w systemie
available_plants = ['Plant1', 'Plant2', 'Plant3']

# Okresy dostępne w systemie
available_periods = ['Period1', 'Period2', 'Period3']

# Katalog, w którym znajdują się pliki SFCR
base_directory = 'sample_data'

# Funkcja do wczytywania danych z plików CSV
def load_data(plant, period, file_type):
    file_path = os.path.join(base_directory, plant, period, f'nazwa_{file_type}.csv')
    df = pd.read_csv(file_path)  # Możesz dostosować sposób wczytywania danych w zależności od rzeczywistego formatu pliku CSV
    return df

# Aplikacja Dash
app = dash.Dash(__name__)

# Układ interfejsu użytkownika
app.layout = html.Div([
    html.H1("Analiza plików SFCR"),
    
    # Wybór zakładu
    html.Label("Wybierz zakład:"),
    dcc.Dropdown(
        id='plant-dropdown',
        options=[{'label': plant, 'value': plant} for plant in available_plants],
        value=available_plants[0]
    ),
    
    # Slider do wyboru okresu
    html.Label("Wybierz okres:"),
    dcc.RangeSlider(
        id='period-slider',
        min=0,
        max=len(available_periods) - 1,
        marks={i: period for i, period in enumerate(available_periods)},
        value=[0, len(available_periods) - 1]
    ),
    
    # Wybór typu pliku do analizy
    html.Label("Wybierz typ pliku:"),
    dcc.RadioItems(
        id='file-type-radio',
        options=[
            {'label': 'Typ 1', 'value': 1},
            {'label': 'Typ 2', 'value': 2},
            {'label': 'Typ 3', 'value': 3}
        ],
        value=1,
        labelStyle={'display': 'block'}
    ),
    
    # Przycisk do analizy plików
    html.Button("Analizuj pliki", id='analyze-button'),
    
    # Wykresy
    dcc.Graph(id='line-plot'),
])

# Funkcja do obsługi interakcji użytkownika i generowania wykresów
@app.callback(
    Output('line-plot', 'figure'),
    [Input('analyze-button', 'n_clicks')],
    [Input('plant-dropdown', 'value')],
    [Input('period-slider', 'value')],
    [Input('file-type-radio', 'value')]
)
def update_plot(n_clicks, selected_plant, selected_periods, selected_file_type):
    # Wczytaj dane dla wybranego zakładu, okresu i typu pliku
    data = []
    for period_index in range(selected_periods[0], selected_periods[1] + 1):
        df = load_data(selected_plant, available_periods[period_index], selected_file_type)
        data.append(df)

    # Przykładowy wykres liniowy (dostosuj go do potrzeb analizy)
    fig = {
        'data': [
            {'x': df.index, 'y': df['Column1'], 'type': 'line', 'name': f'{available_periods[i]}_{selected_file_type}'}
            for i, df in enumerate(data)
        ],
        'layout': {
            'title': 'Wykres analizy plików SFCR',
            'xaxis': {'title': 'Czas'},
            'yaxis': {'title': 'Wartość'}
        }
    }

    return fig

# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run_server(debug=True)