# -*- coding: utf-8 -*-
"""
Title: Customer Map on demographics Data solutions for Exercise 3 (Tabs)
"""
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import dash_table


demographics = pd.read_csv('data/demographics.csv')
demographics["Birthdate"] = pd.to_datetime(demographics["Birthdate"],
                                            format="%d.%m.%Y",
                                            utc=True,
                                            dayfirst=True)

demographics["JoinDate"] = pd.to_datetime(demographics["JoinDate"],
                                            format="%d.%m.%Y",
                                            utc=True,
                                            dayfirst=True)

gender_options = []
for gender in demographics['Gender'].unique():
    gender_options.append({'label':str(gender),
                           'value':gender})

demographics["CustomerCount"] = demographics.groupby(["zip_city"], as_index=False)["Customer"].transform("count")

app = dash.Dash()

#Add the CSS Stylesheet
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

app.layout = html.Div([html.H1('Customer Map', style={'textAlign':'center'}),
                       html.Div(children=[html.Div([html.H3('Inputs'),
                                                   html.H6('Gender'),
                                                   html.P(
                                                           dcc.Checklist(id='gender-picker',
                                                                         options=gender_options,
                                                                         values=['m','f','alien']
                                                                         )
                                                           ),
                                                    html.H6('Join Date'),
                                                    html.P(
                                                            dcc.DatePickerRange(
                                                                    id='date-picker-range',
                                                                    min_date_allowed=min(demographics.JoinDate),
                                                                    max_date_allowed=max(demographics.JoinDate),
                                                                    initial_visible_month=dt(1989, 11, 9),
                                                                    start_date=min(demographics.JoinDate),
                                                                    end_date=max(demographics.JoinDate)
                                                                    )
                                                            )
                                                    ])
                                            ],
                                style = {'float':'left'},
                                className = "two columns"),
                        html.Div([dcc.Tabs(children=[dcc.Tab(label='Map',
                                                            children=html.Div([
                                                                    dcc.Graph(id='CustomerMap')
                                                                    ])
                                                            ),
                                                    dcc.Tab(label='Data',
                                                            children=[html.Div([dash_table.DataTable(
                                                                                id='table',
                                                                                columns = [{"name": i, "id": i} for i in demographics.columns],
                                                                                data = demographics.to_dict("rows")
                                                                )])
                                                                    ]
                                                            )
                                                    ]
                                            )
                                ],
                                className = "nine columns",
                                style = {'float':'right'})
                ]
                )

@app.callback(
    dash.dependencies.Output('CustomerMap', 'figure'),
    [dash.dependencies.Input('gender-picker', 'values'),
     dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date')])

def update_figure(selected_gender, start_date, end_date):    
    filtered_df = demographics[demographics['Gender'].isin(selected_gender)]
    filtered_df = filtered_df.loc[(demographics['JoinDate'] >= start_date) &
                                   (demographics['JoinDate'] <= end_date),]
    filtered_df["CustomerCount"] = filtered_df.groupby(["zip_city"], as_index=False)["Customer"].transform("count")

    customerCount = filtered_df['CustomerCount'].tolist()
    zipcity = filtered_df['zip_city'].tolist()
    hovertext = []
    for i in range(len(customerCount)):
        k = str(zipcity[i]) + ':' + str(customerCount[i])
        hovertext.append(k)
    #only the updated arguments are returned to the figure object, not a figure object itself.
    return {'data':[dict(
                        type = 'scattergeo',
                        locationmode = 'USA-states',
                        lon = filtered_df['zip_longitude'],
                        lat = filtered_df['zip_latitude'],
                        text = hovertext,
                        hoverinfo = 'text',
                        marker = dict(
                        size = filtered_df['CustomerCount'],
                        line = dict(width=0.5, color='rgb(40,40,40)'),
                        sizemode = 'area'
                        ),
                        transforms = [dict(
                        type = 'aggregate',
                        groups = filtered_df['zip_city'],
                        aggregations = [dict(target = filtered_df['Customer'], func = 'count', enabled = True)]
                                        )
                                        ]
                        )
                    ]
            }

#We need another App Callback
    
@app.callback(
    dash.dependencies.Output('table', 'data'),
    [dash.dependencies.Input('gender-picker', 'values'),
     dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date')])

def update_table(selected_gender, start_date, end_date):    
    filtered_df = demographics[demographics['Gender'].isin(selected_gender)]
    filtered_df = filtered_df.loc[(demographics['JoinDate'] >= start_date) &
                                   (demographics['JoinDate'] <= end_date),]
    filtered_df["CustomerCount"] = filtered_df.groupby(["zip_city"], as_index=False)["Customer"].transform("count")
    return filtered_df.to_dict("rows")

if __name__ == '__main__':
    app.run_server()