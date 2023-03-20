from dash import dash, html, dcc, dash_table, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import altair as alt
from vega_datasets import data
import plotly.express as px


# ======================= Import data =======================
temp_df = pd.read_csv('data/processed/temperature_data.csv', index_col=0, parse_dates=True)
ppt_df = pd.read_csv('data/processed/percipitation_data.csv', index_col=0, parse_dates=True)
df = pd.concat((temp_df, ppt_df), axis = 1)
df = df.iloc[:, [0, 1, 3]].copy().iloc[:-1, :] # remove the only 1 record in 2020
df['Year'] = df.index.year

# compute annual mean, min, max
df_sum = df.groupby(by=["Year", "CITY"]).mean().round(2)
df_sum['temp_min'] = df.groupby(by=["Year", "CITY"]).min()['MEAN_TEMP_C']
df_sum['temp_max'] = df.groupby(by=["Year", "CITY"]).max()['MEAN_TEMP_C']
df_sum['ppt_min'] = df.groupby(by=["Year", "CITY"]).min()['TOTAL_PERCIP_mm']
df_sum['ppt_max'] = df.groupby(by=["Year", "CITY"]).max()['TOTAL_PERCIP_mm']
df_sum.rename(columns = {'MEAN_TEMP_C': 'temp_avg', 
                         'TOTAL_PERCIP_mm' : 'ppt_avg'}, inplace = True)
df_sum = df_sum.reset_index('CITY').reset_index('Year')

# replace quebec with quebec city
df_sum['CITY'] = df_sum['CITY'].str.replace('QUEBEC', 'QUEBEC CITY')

# add lon and lat for map
geo_data = pd.DataFrame({'CITY' : ["CALGARY", "EDMONTON", "HALIFAX", "MONCTON", "MONTREAL", "OTTAWA", "QUEBEC CITY",
            "SASKATOON", "STJOHNS", "TORONTO", "VANCOUVER", "WHITEHORSE", "WINNIPEG"],
            'citylat' : [51.0447, 53.5444, 44.6488, 46.0878, 45.5017, 45.4215, 46.8139, 52.1332,
              47.5615, 43.6532, 49.2827, 60.7212, 49.8951],
              'citylon' : [-114.0719, -113.4909, -63.5752, -64.7782, -73.5673, -75.6972, -71.2080,
              -106.6700, -52.7126, -79.3832, -123.1207, -135.0568, -97.1384]
}
)
df_sum = pd.merge(df_sum, geo_data, how = 'left')


# city list
city_lst = df_sum['CITY'].unique().tolist()

# ======================= Style =======================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']) 


# add multi-dropdown
app.layout = html.Div([

    # Title Row
     dbc.Row([
        'Climate Tracker for Canada 🇨🇦'], 
        align="center", 
        justify="center",
        style={"background-color": "rgba(157, 179, 187, 1)",
               "padding": "10px","margin": "10px","width": "100%",
                "height": "80px","opacity": 1,
                'text-align': 'center',
                'font-size': '48px'}
                     ),
                     
    dbc.Row([
        # Widget Col
        dbc.Col([
            dbc.Row([
            dbc.Card([
                dbc.CardHeader('Choose a Type of Data to Start:', style={'fontWeight': 'bold'}),
                dbc.CardBody(dcc.RadioItems( id='radio_button',
                           options=[{'label': 'Temperature (C)', 'value': 'temp'},
                                    {'label': 'Percipitation (mm)', 'value': 'ppt'}],
            value='temp'))], style={"paddingBottom": "20px"})
            ], style = {'paddingBottom': '300px'}),

            dbc.Row([
            dbc.Card([
                dbc.CardHeader('Explore Climate Metrics By City:', style={'fontWeight': 'bold'}),
                dbc.CardBody(dcc.Dropdown(id='city_dropdown',
                         options = [{'label': city, 'value': city} for city in city_lst],
                         value = 'VANCOUVER', 
                         multi = False,
                         placeholder = 'Select one city to explore'))], style={"paddingBottom": "20px"}),

            dbc.Card([
                dbc.CardHeader('Select Year Range to Zoom In the Trend:', style={'fontWeight': 'bold'}),
                dcc.RangeSlider(id='year_slider', min= 1940, 
                                    max=2019,
                                    step=1,
                                    value=[1940,2019],
                                    marks={i: f'{int(i):,}' for i in range(1940, 2020, 10)})
            ], style={"paddingBottom": "20px"})])
            # col stype
            ], style = {"background-color": "rgba(205, 200, 186, 1)",
               "padding": "20px", "margin": "20px", "width": "20%",
               "height": "800px","opacity": 0.9 },
            md=3),
               
        # Plot Col 
        dbc.Col([
            # Map 
            dbc.Row([
                dcc.Graph(id="map")
                ], 
                style={"padding": "0","margin": "0","width": "100%",
                     "height": "400px","opacity": 0.9
                     }
                ),
            # side by side trend plots
            dbc.Row([ 
                dbc.Col([
                    dbc.Card([
                    html.Iframe(id='line_plot',
                    style={'border-width': '0', 'width': '100%', 'height': '400px'})
                ])
                ]),
                dbc.Col([
                    dbc.Card([
                    html.Iframe(id='trend_plot',
                    style={'border-width': '0', 'width': '100%', 'height': '400px'})
                ])
                ])
                ], 
                style={"padding": "0","margin": "0","width": "100%", 
                       "height": "900px","opacity": 0.9})], md= 9)
    ])
])


# ================== Set up callbacks/backend ===================== 
@app.callback(
    [Output('line_plot', 'srcDoc'),
     Output('trend_plot', 'srcDoc'),
     Output('map', 'figure')],
    [Input('year_slider', 'value'),
    Input('city_dropdown', 'value'),
    Input('radio_button', 'value')])
def plot_lineplot(year_range, selected_city, datatype):
    avg_col = datatype + "_avg"
    min_col = datatype + "_min"
    max_col = datatype + "_max"

    if datatype == 'temp':
        title_text = "Annual Min(blue), Average(black) and Max (red) Temperature (C) of " + selected_city
        title_text2 = "Annual Average Temperature (C) Trend of " + selected_city
        col_range = [-8, 12]
        theme_text = 'Temperature (C)'
    else:
        title_text = "Annual Min(blue), Average(black) and Max (red) Percipitation (mm) of " + selected_city
        title_text2 = "Annaul Average Percipitation (mm) Trend of " + selected_city
        col_range = [0, 6.5]
        theme_text = 'Percipitation (mm)'


    # ==== LINE PLOT ======
    lineplot_df = df_sum.query('Year >= @year_range[0] and Year <= @year_range[1] and CITY in @selected_city')

    chart_avg = alt.Chart(lineplot_df, title = title_text).mark_line(color = 'black').encode(
        alt.X('Year', title='Year'),
        alt.Y(avg_col, title = 'Annual values'),
        alt.Tooltip(['Year', avg_col])).interactive()
    
    chart_min = alt.Chart(lineplot_df).mark_line(color = 'blue').encode(
        alt.X('Year', title='Year'),
        alt.Y(min_col),
        alt.Tooltip(['Year', min_col])).interactive()
    
    chart_max = alt.Chart(lineplot_df).mark_line(color = 'red').encode(
        alt.X('Year', title='Year'),
        alt.Y(max_col),
        alt.Tooltip(['Year', max_col])).interactive()
    
    line_chart = chart_avg + chart_min + chart_max
    
    line_fin = line_chart.to_html()

    # ===== Trendline plot =====
    trend_points = alt.Chart(lineplot_df, title = title_text2).mark_circle(color = 'silver').encode(
        alt.X('Year', title='Year', scale=alt.Scale(zero=False)),
        alt.Y(avg_col, scale=alt.Scale(zero=False)),
        alt.Tooltip(['Year', avg_col]))
    
    trend_reg = trend_points.transform_regression('Year', avg_col, groupby = ['CITY']
                                                  ).mark_line(color = 'black', size=3)
    
    trend_plot_fin = alt.layer(trend_points, trend_reg).to_html()


    # ===== MAP ======

    map_fin = px.scatter_geo(df_sum, lon ="citylon", lat = 'citylat', 
                     color= avg_col, 
                     hover_name="CITY",
                     animation_frame="Year",
                     projection="natural earth",
                     range_color=col_range,
                     labels={avg_col: theme_text},
                     center={"lat": 49.8951, "lon": -97.1384},
                     scope = 'north america',
                     basemap_visible=True,
                     title = 'Overall Climate Trend for 13 Canadian Major Cities: Press ▶️ to start the animation',
                     height=400
                     )
    

    return line_fin, trend_plot_fin, map_fin

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)