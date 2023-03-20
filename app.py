from dash import dash, html, dcc, dash_table, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import altair as alt
from vega_datasets import data

# ======================= Import data =======================
temp_df = pd.read_csv('data/processed/temperature_data.csv', index_col=0, parse_dates=True)
ppt_df = pd.read_csv('data/processed/percipitation_data.csv', index_col=0, parse_dates=True)
df = pd.concat((temp_df, ppt_df), axis = 1)
df = df.iloc[:, [0, 1, 3]].copy().iloc[:-1, :] # remove the only 1 record in 2020
df['Year'] = df.index.year

# compute annual mean, min, max
df_sum = df.groupby(by=["Year", "CITY"]).mean()
df_sum['temp_min'] = df.groupby(by=["Year", "CITY"]).min()['MEAN_TEMP_C']
df_sum['temp_max'] = df.groupby(by=["Year", "CITY"]).max()['MEAN_TEMP_C']
df_sum['ppt_min'] = df.groupby(by=["Year", "CITY"]).min()['TOTAL_PERCIP_mm']
df_sum['ppt_max'] = df.groupby(by=["Year", "CITY"]).max()['TOTAL_PERCIP_mm']
df_sum.rename(columns = {'MEAN_TEMP_C': 'temp_avg', 
                         'TOTAL_PERCIP_mm' : 'ppt_avg'}, inplace = True)
df_sum = df_sum.reset_index('CITY').reset_index('Year')

# city list
city_lst = df_sum['CITY'].unique().tolist()

# ======================= Style =======================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']) 


# add multi-dropdown
app.layout = html.Div([
    'Choose type of data:', 
    dcc.RadioItems( id='radio_button',
        options=[
            {'label': 'Temperature (C)', 'value': 'temp'},
            {'label': 'Percipitation (mm)', 'value': 'ppt'}],
        value='temp'
    ),

    'Select cities:', dcc.Dropdown(id='city_dropdown',
                                  options = [{'label': city, 'value': city} for city in city_lst],
                          value = 'VANCOUVER', 
                          multi = False,
                          placeholder = 'Select one city to explore'),

    'Select Year Range to explore the trend:', dcc.Slider(id='year_slider', min= 1940, 
                                    max=2019,
                                    step=1,
                                    value=2019,
                                    marks={i: f'{int(i):,}' for i in range(1940, 2020, 5)}),

    html.Iframe(id='line_plot',
                style={'border-width': '0', 'width': '100%', 'height': '400px'})
                   ]) 

# ================== Set up callbacks/backend ===================== 
# TOTAL_PERCIP_mm
# MEAN_TEMP_C
@app.callback(
    Output('line_plot', 'srcDoc'),
    Input('year_slider', 'value'),
    Input('city_dropdown', 'value'),
    Input('radio_button', 'value'))
def plot_lineplot(xmax, selected_city, datatype):
    avg_col = datatype + "_avg"
    min_col = datatype + "_min"
    max_col = datatype + "_max"

    lineplot_df = df_sum.query('Year <= @xmax and CITY in @selected_city')

    chart_avg = alt.Chart(lineplot_df).mark_line(color = 'black').encode(
        alt.X('Year', title='Year'),
        alt.Y(avg_col, title = 'Annual values'),
        alt.Tooltip(avg_col)).interactive()
    
    chart_min = alt.Chart(lineplot_df).mark_line(color = 'blue').encode(
        alt.X('Year', title='Year'),
        alt.Y(min_col),
        alt.Tooltip(min_col)).interactive()
    
    chart_max = alt.Chart(lineplot_df).mark_line(color = 'red').encode(
        alt.X('Year', title='Year'),
        alt.Y(max_col),
        alt.Tooltip(max_col)).interactive()
    
    line_chart = chart_avg + chart_min + chart_max
    
    return line_chart.to_html()


if __name__ == '__main__':
    app.run_server(debug=True)