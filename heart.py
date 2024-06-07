import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import base64

app = dash.Dash(__name__)

# Load the dataset
df = pd.read_csv('heart_disease_data.csv')

# Table figure
table = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns),
                fill_color='paleturquoise',
                align='left',
                font=dict(size=14)),
    cells=dict(values=[df[col] for col in df.columns],
               fill_color='lavender',
               align='left',
               font=dict(size=12))
)])

table.update_layout(
    title_text="Heart Disease Dataset Table",
    title_x=0.5,
    width=1000,
    height=600
)

# Slope data and figure
slope_data = {
    "flat": 345,
    "upsloping": 203,
    "downsloping": 63
}

slope_fig = go.Figure()
slope_fig.add_trace(go.Scatter(x=list(slope_data.keys()), y=list(slope_data.values()), mode='lines+markers', name='Slope'))
slope_fig.update_layout(
    title="Slope of the Peak Exercise ST Segment",
    xaxis_title="Slope Type",
    yaxis_title="Count",
    showlegend=True
)

color_map = {
    'male': 'blue',
    'female': 'red'
}

# Create the Sunburst figure
sunburst_fig = px.sunburst(df,
                           path=['sex', 'heart_disease_category'],
                           color_discrete_map=color_map,
                           title='Heart Disease Breakdown by Gender and Category')

# Convert the heart image to base64
image_filename = 'Health.jpg'  # Replace with your image file path
encoded_image = base64.b64encode(open(image_filename, 'rb').read()).decode()

# Create the box plot figure
box_plot_fig = px.box(data_frame=df, x='sex', y='oldpeak', color='sex')
box_plot_fig.update_layout(title="Box Plot of Oldpeak by Sex")

# App layout
app.layout = html.Div([
    html.H1("Heart Disease Data Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Img(src='data:image/png;base64,{}'.format(encoded_image), style={'width': '300px', 'height': '300px'})
    ], style={'textAlign': 'center'}),

    dcc.Graph(id='table', figure=table),

    dcc.Dropdown(
        id='feature-dropdown',
        options=[
            {'label': 'Cholesterol', 'value': 'chol'},
            {'label': 'Resting Blood Pressure', 'value': 'trestbps'},
            {'label': 'Rest ECG', 'value': 'restecg'}
        ],
        value='restecg',
        clearable=False
    ),

    html.Div([
        dcc.Graph(id='histogram')
    ], className="six columns"),

    html.Div([
        dcc.Graph(id='scatter-plot')
    ], className="six columns"),

    html.Div([
        dcc.Checklist(
            id='plot-options',
            options=[
                {'label': 'Include Age Plot', 'value': 'cp'},
                {'label': 'Include CP Plot', 'value': 'seaborn'},
                {'label': 'Include Slope Plot', 'value': 'slope'},
                {'label': 'Include Sunburst Plot', 'value': 'sunburst'}
            ],
            value=['cp', 'seaborn', 'slope', 'sunburst']
        ),
        html.Div(id='histogram-cp-container'),
        html.Div(id='seaborn-container'),
        html.Div(id='new-scatter-plot-container'),
        html.Div(id='slope-plot-container'),
        html.Div(id='sunburst-plot-container'),
        html.Div(id='bar-plot-container'),
        html.Div([
            dcc.Graph(id='box-plot', figure=box_plot_fig)
        ], className="six columns")
    ], className="twelve columns")
])

# Callbacks
@app.callback(
    Output('histogram', 'figure'),
    Input('feature-dropdown', 'value')
)
def update_histogram(selected_feature):
    fig = px.histogram(df, x=selected_feature, color='heart_disease_category', barmode='overlay')
    fig.update_layout(title=f'Histogram of {selected_feature}', xaxis_title=selected_feature, yaxis_title='Count')
    return fig

@app.callback(
    Output('scatter-plot', 'figure'),
    Input('feature-dropdown', 'value')
)
def update_scatter(selected_feature):
    fig = px.scatter(df, x=selected_feature, y='thalch', color='heart_disease_category',
                     title=f'Scatter Plot of {selected_feature} vs Max Heart Rate (thalch)',
                     labels={selected_feature: selected_feature, 'thalch': 'Max Heart Rate'})
    return fig

@app.callback(
    Output('histogram-cp-container', 'children'),
    Input('plot-options', 'value')
)
def update_histogram_cp(selected_options):
    if 'cp' in selected_options:
        fig = px.histogram(df, x="age", color="cp")
        fig.update_layout(title='Histogram of Age by Chest Pain Type (CP)')
        return dcc.Graph(id='histogram-cp', figure=fig)
    else:
        return None

@app.callback(
    Output('seaborn-container', 'children'),
    Input('plot-options', 'value')
)
def update_seaborn_plot(selected_options):
    if 'seaborn' in selected_options:
        colors = ['#4e73df', '#e83e8c', '#f6c23e', '#1cc88a']
        fig = px.histogram(df, x='cp', color='dataset', barmode='group', color_discrete_sequence=colors)
        fig.update_layout(
            title='Count Plot of CP by Dataset',
            xaxis_title='CP',
            yaxis_title='Count',
            bargap=0.2
        )
        return dcc.Graph(id='seaborn-plot', figure=fig)
    else:
        return None

@app.callback(
    Output('new-scatter-plot-container', 'children'),
    Input('feature-dropdown', 'value')
)
def update_new_scatter_plot(selected_feature):
    if selected_feature == 'trestbps':
        fig = px.scatter(df, x='age', y='trestbps', color='sex',
                         title='Scatter Plot of Age vs Resting Blood Pressure by Sex',
                         labels={'age': 'Age', 'trestbps': 'Resting Blood Pressure'})
        return dcc.Graph(id='new-scatter-plot', figure=fig)
    else:
        return None

@app.callback(
    Output('slope-plot-container', 'children'),
    Input('plot-options', 'value')
)
def update_slope_plot(selected_options):
    if 'slope' in selected_options:
        return dcc.Graph(id='slope-plot', figure=slope_fig)
    else:
        return None

@app.callback(
    Output('sunburst-plot-container', 'children'),
    Input('plot-options', 'value')
)
def update_sunburst_plot(selected_options):
    if 'sunburst' in selected_options:
        return dcc.Graph(id='sunburst-plot', figure=sunburst_fig)
    else:
        return None

@app.callback(
    Output('bar-plot-container', 'children'),
    Input('feature-dropdown', 'value')
)
def update_bar_plot(selected_feature):
    if selected_feature == 'restecg':
        fig = px.bar(df, x='dataset', color='sex', title='Bar Plot of Dataset by Sex')
        return dcc.Graph(id='bar-plot', figure=fig)
    else:
        return None

if __name__ == '__main__':
    app.run_server(debug=True)







