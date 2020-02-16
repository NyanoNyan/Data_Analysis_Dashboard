import os
import pandas as pd
import psycopg2 as pg2

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

s3 = os.environ['DB_USER']
s4 = os.environ['DB_PASS']
s5 = os.environ['DB_HOST']
s6 = os.environ['DB_PORT']

conn = pg2.connect(database='d3qt146nb6jovo', user=s3, password=s4,
                   host=s5, port=s6)
cur = conn.cursor()

# Get the data From postgres
sql2 = "SELECT * FROM pg_catalog.pg_tables \
        WHERE schemaname != 'pg_catalog' \
        AND schemaname != 'information_schema';"
dat2 = pd.read_sql_query(sql2, conn)


# Checking purposes
# sql_store = "SELECT * FROM customer"
# store_d = pd.read_sql_query(sql_store, conn)

# Get the film data + it's genres

sql_store = "SELECT f.title, f.release_year, f.rental_duration,f.rental_rate,f.length,f.replacement_cost,f.rating,f.special_features,c.name \
             FROM film AS f\
             INNER JOIN film_category AS fc ON f.film_id=fc.film_id\
             INNER JOIN category AS c ON c.category_id = fc.category_id"
             

store_d = pd.read_sql_query(sql_store, conn)
#store_d.head()

conn.close()

store_d.rename(columns={'name':'genre'}, inplace=True)

# Plot for number of movies which have specific ratings

# store_d.groupby('rating')['rating'].count().plot(kind = 'bar')
ll = store_d.groupby('rating')['rating'].count()


# Dashboard
app = dash.Dash()
server = app.server

app.layout = html.Div(children=[
    html.H1(children='Testing Dashboard'),
    html.H2(children='Interactive plots for a dvd rental database from SQL'),



    html.Div(children='''
        Please select an option
    '''),

    dcc.Dropdown(
        id='demo-dropdown',
        options=[
            {'label': 'Show all', 'value': 'ALL'},
            {'label': 'Rated R', 'value': 'R'},
            {'label': 'Parental guidance', 'value': 'PG'},
            {'label': 'Parental guidance 13 (PG-13)', 'value': 'PG-13'},
            {'label': 'No Children 17 and Under Admitted', 'value': 'NC-17'},
            {'label': 'General Audiences', 'value': 'G'}

        ],
        value='ALL',
        placeholder="Select a Rating",
    ),
    html.Div(id='dd-output-container')
])

@app.callback(
    Output(component_id='dd-output-container', component_property='children'),
    [Input(component_id='demo-dropdown', component_property='value')])

def update_output(value):

    if value == 'ALL':
        ll = store_d.groupby(['genre','rating'])['rating'].count()
        ll = ll.unstack()
        #val = ll['G':]

        testing1 = dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': ll.index, 'y': ll['R'], 'legend': ll.index, 'type': 'bar', 'name': 'R'},
                    {'x': ll.index, 'y': ll['PG'], 'legend': ll.index, 'type': 'bar', 'name': 'PG'},
                    {'x': ll.index, 'y': ll['PG-13'], 'legend': ll.index, 'type': 'bar', 'name': 'PG-13'},
                    {'x': ll.index, 'y': ll['NC-17'], 'legend': ll.index, 'type': 'bar', 'name': 'NC-17'},
                    {'x': ll.index, 'y': ll['G'], 'legend': ll.index, 'type': 'bar', 'name': 'G'},
                ],
                'layout': {
                    'title': 'Total rating counts of movies for: ' + value
                }
            }
        )
    else:
        ll = store_d.groupby(['genre','rating'])['rating'].count()
        ll = ll.unstack()
        yval = ll[value]
        #s = str(value)
        #ll = ll.loc[s]
        testing1 = dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': ll.index, 'y': yval, 'type': 'bar', 'name': 'R'},
                ],
                'layout': {
                    'title': 'Total rating counts of movies for: ' + value
                }
            }
        )

    return testing1
if __name__ == '__main__':
    app.run_server(debug=True)
