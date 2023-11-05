from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash_draggable

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash(__name__)
app.layout = html.Div([
    html.H1(children='Численность стран планеты Земля', style={'textAlign':'center'}),
    dcc.Dropdown(
        options=[{'label': country, 'value': country} for country in df.country.unique()],
        value=['Canada'],
        id='dropdown-selection',
        multi=True,
        persistence='local'
    ),
    dcc.Dropdown(
        options=[
            {'label': 'Ожидаемая продолжительность жизни', 'value': 'lifeExp'},
            {'label': 'Население', 'value': 'pop'},
            {'label': 'ВВП на душу населения', 'value': 'gdpPercap'}
        ],
        value='pop',
        id='dropdown-measure',
        persistence='local'
    ),
    dash_draggable.ResponsiveGridLayout([
        dcc.Graph(id='graph-content'),
        dcc.Graph(id='top-population'),
        dcc.Graph(id='bubble-chart'),
        dcc.Graph(id='pie-chart')
    ]),
    dcc.Dropdown(
        options=[{'label': year, 'value': year} for year in df.year.unique()],
        value=2007,
        id='year-selector',
        persistence='local'
    ),
    dcc.Dropdown(
        options=[
            {'label': 'Ожидаемая продолжительность жизни', 'value': 'lifeExp'},
            {'label': 'Население', 'value': 'pop'},
            {'label': 'ВВП на душу населения', 'value': 'gdpPercap'}
        ],
        multi=True,
        value=['lifeExp', 'pop'],
        id='bubble-chart-measure',
        persistence='local'
    ),
    dcc.Input(id='population-min', type='number', placeholder='Минимальная численность населения'),
    dcc.Input(id='population-max', type='number', placeholder='Максимальная численность населения')
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('dropdown-measure', 'value')
)
def update_graph(selected_countries, measure):
    dff = df[df.country.isin(selected_countries)]
    figure = px.line(dff, x='year', y=measure, color='country')
    figure.update_xaxes(title_text='Год')
    figure.update_yaxes(title_text='Население')
    return figure
@callback(
    Output('bubble-chart', 'figure'),
    Input('bubble-chart-measure', 'value'),
    Input('year-selector', 'value'),
    Input('population-min', 'value'),
    Input('population-max', 'value')
)
def update_bubble_chart(selected_measures, year, population_min, population_max):
    if len(selected_measures) < 2:
        return {}
    dff = df[df.year == year]
    selected_radius = 'pop'
    population_min = int(population_min) if population_min else min(df['pop'])
    population_max = int(population_max) if population_max else max(df['pop'])
    dff = dff[(dff['pop'] >= population_min) & (dff['pop'] <= population_max)]
    return px.scatter(
        dff,
        x=selected_measures[0],
        y=selected_measures[1],
        size=selected_radius,
        color='country',
        text='country',
        labels={selected_measures[0]: selected_measures[0], selected_measures[1]: selected_measures[1]}
    )
@callback(
    Output('top-population', 'figure'),
    Input('dropdown-measure', 'value'),
    Input('year-selector', 'value')
)
def update_bar_chart(measure, year):
    dff = df[df.year == year]
    top_15 = dff.groupby('country').sum()[[measure]].sort_values(measure, ascending=False).head(15)
    figure1 = px.bar(top_15, x=top_15.index, y=measure)
    figure1.update_xaxes(title_text='Страна')
    figure1.update_yaxes(title_text='Население')
    return figure1

@callback(
    Output('pie-chart', 'figure'),
    Input('year-selector', 'value')
)
def update_pie_chart(year):
    dff = df[df.year == year]
    continent_population = dff.groupby('continent').sum()['pop']
    return px.pie(continent_population, names=continent_population.index, values=continent_population)

if __name__ == '__main__':
    app.run(debug=True)
