# import
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

import plotly.express as ex
import pandas as pd
import petl as etl

import io
import base64

# pip3 install dash_bootstrap_components
import dash_bootstrap_components as dbc


dataframe = None

# initialisation
app = dash.Dash('', external_stylesheets=[dbc.themes.BOOTSTRAP])



"""
upload ->dcc.upload
configure-> label, dropdownlist, button


viaualise ->graph

"""





app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            # Allow multiple files to be uploaded
                            multiple=True
                        ), 
                        html.Br(),
                        html.Br(),
                        html.Span(id='upload-summary'), 
                        html.Br(),
                        dcc.RangeSlider(
                            step = 1,
                            min = 2000,
                            max = 2021,
                            value=[2010, 2015],
                            id='year-selection'
                        ),
                        html.Br(),
                        html.Span('selection: 2010 - 2015', id='range-selection')
                    ]), md=5, className='sidebar'
                ),
                dbc.Col(
                    html.Div([
                        dcc.Graph(id='visualisation', figure={})
                    ]), md=7
                ),
            ]
        )
    ])


@app.callback(
    Output(component_id='upload-summary', component_property='children'),
    Output(component_id='visualisation', component_property='figure'),
    Output(component_id='year-selection', component_property='min'),
    Output(component_id='year-selection', component_property='max'),
    Output(component_id='year-selection', component_property='value'),
    Output(component_id='range-selection', component_property='children'),
    Input(component_id='year-selection', component_property='value'),
    Input(component_id='upload-data', component_property='contents'),
    State(component_id='upload-data', component_property='filename')
)
def get_upload_summary(selection, uploaded_files,  names_of_files):
    global dataframe
    if (uploaded_files and names_of_files) and dataframe is not None:
        for index in range(0, len(uploaded_files)):
            uploaded_file = uploaded_files[index]
            uploaded_file_name =  names_of_files[index]
            #data:text/csv;base64,eWadeferferv.......
            file_type, file_in_base64 = uploaded_file.split(',')
            # initialisation
            decoded_file = base64.b64decode(file_in_base64)
            file_as_stream = io.StringIO(decoded_file.decode('unicode-escape'))
            uploaded_file_df = pd.read_csv(file_as_stream)
            dataframe =  pd.concat([uploaded_file_df])

            # get the years
            tbl = etl.fromdataframe(uploaded_file_df)
            tbl = etl.convert(tbl, 'year', int)
            start_year, end_year =  etl.limits(tbl, 'year')
            
            
            filtered_df =  uploaded_file_df[uploaded_file_df['year'] == start_year]
            
            figure = ex.bar(filtered_df, x='month', y='sales')
            return uploaded_file_name, figure, start_year, end_year, [start_year, start_year], f'selection: {start_year} - {start_year}'
        

        #data:text/csv;base64,eWVhcixtb250a
    
    elif selection is not None and len(selection) > 0 and dataframe is not None:
        start_year =  selection[0]
        end_year = selection[1]
        tbl = etl.fromdataframe(dataframe)
        tbl = etl.convert(tbl, 'year', int)
        start_year, end_year =  etl.limits(tbl, 'year')
        filtered_df =  dataframe[ start_year <= dataframe['year'] <= end_year ]
        figure = ex.bar(filtered_df, x='month', y='sales')

        return '', figure, start_year, end_year, selection, f'selection: {selection[0]} - {selection[1]}'
    
    return "", {}, 2000, 2021, [2005, 2015], 'selection: 2010 - 2015'
    



# running
app.run_server(debug=True)
