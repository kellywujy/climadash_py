from dash import dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

# Import data
temp_df = pd.read_csv('data/processed/temperature_data.csv', index_col=0, parse_dates=True)
ppt_df = pd.read_csv('data/processed/percipitation_data.csv', index_col=0, parse_dates=True)
df = pd.concat((temp_df, ppt_df), axis = 1)
df = df.iloc[:, [0, 1, 3]].copy()
df['Year'] = df.index.year
df_sum = df.groupby(by=["Year", "CITY"]).mean().reset_index('CITY')
city_lst = df_sum['CITY'].unique().tolist()

# Style
# app = dash.Dash(__name__, 
#                 external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__, 
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']) 


# add multi-dropdown
app.layout = html.Div([
    'Select cities',
             dcc.Dropdown(options = city_lst,
                          value = 'VANCOUVER', 
                          multi = True,
                          placeholder = 'Select one or more cities')
                   ]) 
       

if __name__ == '__main__':
    app.run_server(debug=True)

# app.layout = html.Div([
#     html.H1('Canadian Climate Data, 1940 - 2019'),
#     dcc.Dropdown(
#         id='city-dropdown',
#         options=[{'label': city, 'value': city} for city in df['City'].unique()],
#         value='Toronto'
#     ),
#     dcc.Graph(id='temperature-graph'),
#     dcc.Graph(id='precipitation-graph')
# ])
