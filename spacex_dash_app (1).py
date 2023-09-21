import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
spacex_df.columns = [i.replace(' ','_') for i in spacex_df.columns]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for 
                                dcc.Dropdown(id='site-dropdown',
                                   options=[{'label': 'All Sites', 'value': 'Allsites'},
                                            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}],
                                    #value='Allsites',
                                    placeholder='select sites',
                                    searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=0,max=10000,step=1000,
                                                marks={0:'0', 2000:'2000', 4000:'4000', 6000:'6000', 8000:'8000', 10000:'10000'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'Allsites':
       fig = px.pie(spacex_df,values='class',names='Launch_Site',title='Success Rate of all Launch Sites')
       return fig        
    else:
        fd = spacex_df[spacex_df['Launch_Site'] == entered_site]
        fd = fd['Launch_Site'].groupby(spacex_df['class']).count().reset_index()
        fig = px.pie(fd, values='Launch_Site', names='class', title='Success Rate of selected Launch Sites')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),Input(component_id='site-dropdown', component_property='value'),
            Input(component_id='payload-slider', component_property='value'))
def get_graf (entered_site, Range):
    low, high = Range
    scatt_data = spacex_df[spacex_df['Payload_Mass_(kg)'].apply(lambda x : x > low and x < high)].reset_index()
    if entered_site == 'Allsites':
        scatt_fig = px.scatter(scatt_data, x= 'Payload_Mass_(kg)', y='class', color='Booster_Version',
                               title='Success correlation by Payload Mass & BoosterVersion')
        return scatt_fig
    else:
        scatt_data = scatt_data[spacex_df['Launch_Site']== entered_site].reset_index()
        scatt_data = scatt_data.groupby(['Launch_Site','class', 'Booster_Version'])['Payload_Mass_(kg)'].sum().reset_index()
        scatt_fig = px.scatter(scatt_data, x= 'Payload_Mass_(kg)', y='class', color='Booster_Version',
                               title='Success correlation by Payload Mass & BoosterVersion')
        return scatt_fig
# Run the app
if __name__ == '__main__':
    app.run_server()