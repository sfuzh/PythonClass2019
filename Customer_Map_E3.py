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
import io
import flask

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
                                                            ),
                                                    dcc.Tab(label='Export Data',
                                                            children=html.Div([
                                                                    html.A(html.Button('Download', id='download-button')
                                                                    , id='download-link')
                                                                    ])
                                                            ),
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

@app.callback(
    dash.dependencies.Output('download-link', 'href'),
    [dash.dependencies.Input('gender-picker', 'values'),
     dash.dependencies.Input('joindate', 'start_date'),
     dash.dependencies.Input('joindate', 'end_date'),
     dash.dependencies.Input('birthdate', 'start_date'),
     dash.dependencies.Input('birthdate', 'end_date'),
     dash.dependencies.Input('state-picker', 'value')])

#This function creates the download link  
def update_link(selected_gender, join_start_date, join_end_date, birthdate_start_date, birthdate_end_date, selected_state):
    return '/dash/urlToDownload?value={}/{}/{}/{}/{}/{}'.format('-'.join(selected_gender),
                                                                  dt.strptime(join_start_date,'%Y-%M-%d'),
                                                                  dt.strptime(join_end_date,'%Y-%M-%d'),
                                                                  dt.strptime(birthdate_start_date,'%Y-%M-%d'),
                                                                  dt.strptime(birthdate_end_date,'%Y-%M-%d'),
                                                                  '-'.join(selected_state))

#This function performs the csv download, or more precisely it updates the csv that the user downloads.
@app.server.route('/dash/urlToDownload')
def download_csv():
    value = flask.request.args.get('value')
    value = value.split('/')
    #Catch the filters from the downloadlink
    selected_gender = value[0].split('-')
    selected_state = value[5].split('-')
    join_start_date = value[1]
    join_end_date = value[2]
    birthdate_start_date = value[3]
    birthdate_end_date = value[4]
    
    filtered_df = demographics[demographics['Gender'].isin(selected_gender)]
    filtered_df = filtered_df[filtered_df['zip_state'].isin(selected_state)]
    filtered_df = filtered_df.loc[(demographics['JoinDate'] >= join_start_date) &
                                  (demographics['JoinDate'] <= join_end_date) &
                                  (demographics['Birthdate'] >= birthdate_start_date) &
                                  (demographics['Birthdate'] <= birthdate_end_date),]
    filtered_df["CustomerCount"] = filtered_df.groupby(["zip_city"], as_index=False)["Customer"].transform("count")
    
    #if you use Python 2, use io.BytesIO
    str_io = io.StringIO()
    filtered_df.to_csv(str_io)

    mem = io.BytesIO()
    mem.write(str_io.getvalue().encode('utf-8'))
    mem.seek(0)
    str_io.close()
    return flask.send_file(mem,
                       mimetype='text/csv',
                       attachment_filename='downloadFile.csv',
                       as_attachment=True)

if __name__ == '__main__':
    app.run_server()
