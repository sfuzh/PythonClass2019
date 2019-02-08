# -*- coding: utf-8 -*-
"""
Title: Customer Map on demographics Data solutions for Exercise 3 (Tabs)
"""
# import os
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import dash_table

#os.chdir('C:/Users/patri/Dropbox/Python Advanced - Slides & Code/data')

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

state_options = []
for state in demographics['zip_state'].unique():
    state_options.append({'label':str(state),
                           'value':state})
    
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
                                                                    id='joindate',
                                                                    min_date_allowed=min(demographics.JoinDate),
                                                                    max_date_allowed=max(demographics.JoinDate),
                                                                    initial_visible_month=dt(1989, 11, 9),
                                                                    start_date=min(demographics.JoinDate),
                                                                    end_date=max(demographics.JoinDate)
                                                                    )
                                                            ),
                                                    html.H6('Birthdate'),
                                                    html.P(
                                                            dcc.DatePickerRange(
                                                                    id='birthdate',
                                                                    min_date_allowed=min(demographics.Birthdate),
                                                                    max_date_allowed=max(demographics.Birthdate),
                                                                    initial_visible_month=dt(1989, 11, 9),
                                                                    start_date=min(demographics.Birthdate),
                                                                    end_date=max(demographics.Birthdate)
                                                                    )
                                                            ),
                                                    html.H6('State'),
                                                    html.P(dcc.Dropdown(id='state-picker',
                                                                         options=state_options,
                                                                         multi=True,
                                                                         value= demographics['zip_state'].unique().tolist()
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
     dash.dependencies.Input('joindate', 'start_date'),
     dash.dependencies.Input('joindate', 'end_date'),
     dash.dependencies.Input('birthdate', 'start_date'),
     dash.dependencies.Input('birthdate', 'end_date'),
     dash.dependencies.Input('state-picker', 'value')])

def update_figure(selected_gender, join_start_date, join_end_date, birthdate_start_date, birthdate_end_date, selected_state):    
     filtered_df = demographics.loc[(demographics['Gender'].isin(selected_gender)) &
                                    demographics['zip_state'].isin(selected_state) &
                                  (demographics['JoinDate'] >= join_start_date) &
                                  (demographics['JoinDate'] <= join_end_date) &
                                  (demographics['Birthdate'] >= birthdate_start_date) &
                                  (demographics['Birthdate'] <= birthdate_end_date),]
     zip_size = filtered_df.groupby(["zip_city"]).size()

    
     zip_size = filtered_df.groupby(["zip_city", 'zip_longitude', 'zip_latitude']).size()
    
     zipcity = zip_size.index.get_level_values("zip_city").tolist() 
     customerCount = zip_size.values.tolist()
     
     hovertext = []
     for i in range(len(customerCount)):
          k = str(zipcity[i]) + ':' + str(customerCount[i])
          hovertext.append(k)    #only the updated arguments are returned to the figure object, not a figure object itself.
     
     return {'data':[dict(
                        type = 'scattergeo',
                        locationmode = 'USA-states',
                        lon = zip_size.index.get_level_values("zip_longitude").tolist(),
                        lat = zip_size.index.get_level_values("zip_latitude").tolist(),
                        text = hovertext,
                        hoverinfo = 'text',
                        marker = dict(
                        size = customerCount,
                        line = dict(width=0.5, color='rgb(40,40,40)'),
                        sizemode = 'area'
                        )
                        )
                    ],
            'layout': dict(
                      geo = dict(
                                scope='usa',
                                showland = True,
                                landcolor = 'rgb(217, 217, 217)',
                                subunitwidth=1,
                                subunitcolor="rgb(255, 255, 255)"
                                
                                 )
                      )}

#We need another App Callback
    
@app.callback(
    dash.dependencies.Output('table', 'data'),
    [dash.dependencies.Input('gender-picker', 'values'),
     dash.dependencies.Input('joindate', 'start_date'),
     dash.dependencies.Input('joindate', 'end_date'),
     dash.dependencies.Input('birthdate', 'start_date'),
     dash.dependencies.Input('birthdate', 'end_date'),
     dash.dependencies.Input('state-picker', 'value')])

def update_table(selected_gender, join_start_date, join_end_date, birthdate_start_date, birthdate_end_date, selected_state):
    filtered_df = demographics.loc[(demographics['Gender'].isin(selected_gender)) &
                                    demographics['zip_state'].isin(selected_state) &
                                  (demographics['JoinDate'] >= join_start_date) &
                                  (demographics['JoinDate'] <= join_end_date) &
                                  (demographics['Birthdate'] >= birthdate_start_date) &
                                  (demographics['Birthdate'] <= birthdate_end_date),]
        
    return filtered_df.to_dict("rows")

if __name__ == '__main__':
    app.run_server()
