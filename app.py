#importando las librerias para server dash+flask
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.dependencies import Input, Output

#importando las librerias para trabajar con los datos y los modelos
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.interpolate import griddata

#inializando las variables para las bases de datos
db_radiacion = './db/radiacion.db'
db_temperatura = './db/temperatura.db'
db_humedad = './db/humedad.db'

class Sensor():
    def __init__(self):
        self.sensorID = []
        self.sensorTime = []
        self.values = []
        self.sensorLat = []
        self.sensorLon = []

def leerdb_sensor(sensorid, db):
    con = sqlite3.connect(db)
    curs = con.cursor()
    sensorID = []
    sensorTime = []
    sensorVal = []
    sensorLat = []
    sensorLon = []
    for fila in curs.execute("SELECT * FROM data WHERE idsensor='" + sensorid + "'"):
        sensorID.append(fila[0])
        sensorTime.append(fila[1])
        sensorVal.append(fila[2])
        sensorLat.append(fila[3])
        sensorLon.append(fila[4])
    con.close()
    datasensor = Sensor()
    datasensor.sensorID = sensorID
    datasensor.sensorTime = sensorTime
    datasensor.values = sensorVal
    datasensor.Lat = sensorLat
    datasensor.Lon = sensorLon
    return datasensor
#leer sensor de radiacion (es uno solo)
s_rad = leerdb_sensor("S_RS_ext_C01",db_radiacion)
#leer los sensores de humedad y radiacin (son 5x10) en una matriz
w, h = 5, 10; #calculando el x,y
#inicializando matrices
Temp = [[0 for y in range(h)] for x in range(w)]
Hum = [[0 for y in range(h)] for x in range(w)]

#leyendo de la base de datos y asignando a la matriz
for x in range(w):
    for y in range(h):
        Temp[x][y] = leerdb_sensor("s_inv_" + str(x) +"_cam_" + str(y),db_temperatura)
        Hum[x][y] = leerdb_sensor("s_inv_" + str(x) +"_cam_" + str(y),db_humedad)

# Initialize the app
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

dict_list = []
dict_list.append({'label': 'radiacion', 'value': 'radiacion'})
dict_list.append({'label': 'temperatura', 'value': 'temperatura'})
dict_list.append({'label': 'humedad', 'value': 'humedad'})

dict_list2 = []
dict_list2.append({'label': 'Cama 1', 'value': 0})
dict_list2.append({'label': 'Cama 2', 'value': 1})
dict_list2.append({'label': 'Cama 3', 'value': 2})
dict_list2.append({'label': 'Cama 4', 'value': 3})
dict_list2.append({'label': 'Cama 5', 'value': 4})
dict_list2.append({'label': 'Cama 6', 'value': 5})
dict_list2.append({'label': 'Cama 7', 'value': 6})
dict_list2.append({'label': 'Cama 8', 'value': 7})
dict_list2.append({'label': 'Cama 9', 'value': 8})
dict_list2.append({'label': 'Cama 10', 'value': 9})

#mostrando los invernaderos como Cards del formato de dash
def create_invernadero(title, Crad, Ctemp, Chum, info,suma,suma1,men1,men2):
    invernadero = dbc.Card([
        dbc.CardHeader(title),
        dbc.CardBody(
            [
                html.P("Radiacion = "+Crad +" W/m2"),
                html.P("Temperatura = "+Ctemp + " C"),
                html.P("Humedad = "+Chum + " %"),
                html.Hr(),
                html.P("Radiacion total en el dia = "+suma +" W/s"),
                html.P("Radiacion faltante en el dia = "+suma1 +" W/s "),
                html.Hr(),
                html.P("Semaforo en = "+ men1),
                html.P("Observacion = "+men2)
                ]
        )],color="secondary", inverse=True

    )
    return(invernadero)


graphRow1 = dbc.Row([dbc.Col(dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True),width=8),
                     dbc.Col(dcc.Dropdown(id='varselector', options=dict_list,
                                  multi=False,
                                  value='humedad',
                                  className='stockselector'
                                  ),width=2),
                      dbc.Col(dcc.Dropdown(id='camSelector', options=dict_list2,
                                  multi=False,
                                  value=0,
                                  className='stockselector'

                      ),width=2)], className = "mb-4")

slider_time=dcc.Slider(
    id='my_daq_slider_ex',
    min=0,
    max=7,
    step=0.5,
    marks={
        0: '26 Marzo',
        1: '27 Marzo',
        2: '28 Marzo',
        3: '29 Marzo',
        4: '30 Marzo',
        5: '31 Marzo',
        6: '1 Abril ',
        7: 'Ultimo'
    },
    value=7)

invernadero = create_invernadero("Invernadero Cama 1",str(s_rad.values[-1]), str(Temp[0][0].values[-1]),str(Hum[0][0].values[-1]),str(0)+"_"+str(0)+"_"+str(-1),"0", "0" , " ", " ")

graphRow0 = dbc.Row([dbc.Col(invernadero, width=3),
], className = "mb-4",)
    
graphRow2 = dbc.Row(dbc.Col(slider_time,width=9))

app.layout = html.Div([
    html.Div([]),
    html.H1('Trabajo Final IoT'),
    html.Div([html.P('Aplicacion que muestra el tablero de control y modelos de un invernadero de flores '),
        html.P('Trabajo elaborado por: Santiago Restrepo L + Profesor: Leonardo Betancur A. PhD'),
        html.P('Mayo 5 de 2020')]),
    html.Div([ slider_time,
    html.Div(id='slider-output')]),
    dcc.Dropdown(id='demo_dropdown',
        options=[
            {'label': 'Invernadero 1', 'value': '0'},
            {'label': 'Invernadero 2', 'value': '1'},
            {'label': 'Invernadero 3', 'value': '2'},
            {'label': 'Invernadero 4', 'value': '3'},
            {'label': 'Invernadero 5', 'value': '4'},
        ],
        value='0'),
    html.Div([ 
        html.Div(id='slide')]),

   graphRow1
])




@app.callback(Output('slide', 'children'), [Input('my_daq_slider_ex', 'value'), 
                                            Input('demo_dropdown', 'value')])
def update_output(my_daq_slider_ex,demo_dropdown):
    inver = int(demo_dropdown)
    fechaSelected = '2020-04-01' 
    if (my_daq_slider_ex == 0):
        fechaSelected = '2020-03-26' 
    elif (my_daq_slider_ex == 1):
        fechaSelected = '2020-03-27' 
    elif (my_daq_slider_ex == 2):
        fechaSelected = '2020-03-28' 
    elif (my_daq_slider_ex == 3):
        fechaSelected = '2020-03-29' 
    elif (my_daq_slider_ex == 4):
        fechaSelected = '2020-03-30' 
    elif (my_daq_slider_ex == 5):
        fechaSelected = '2020-03-31' 
    elif (my_daq_slider_ex == 6):
        fechaSelected = '2020-04-01' 
    elif (my_daq_slider_ex == 7):
        fechaSelected = '2020-04-01' 
    
    point = -1
    suma=0
    restante = 670000
    for x in range(len(Temp[0][0].sensorTime)):
        if (Temp[0][0].sensorTime[x].split()[0] == fechaSelected):
            point = x
    posiciones = []

    for y in range(len(s_rad.values)):
        if (s_rad.sensorTime[y].split()[0] == fechaSelected):
            posiciones.append(y)
            suma += s_rad.values[y]
    suma1 = restante - suma

    if(suma1 <0):
        suma1 = 0

    mensaje = []
    mensajextra = []
    for j in range(10):
        if (Temp[inver][j].values[point] < 6):
            mensaje.append("Amarillo")
            mensajextra.append("No se puede regar la planta por debajo de los 6 grados")
        elif (Temp[inver][j].values[point] > 32):
            mensaje.append("Rojo")
            mensajextra.append("Se debe de regar la planta 5 minutos cada hora")
        else:
            mensaje.append("Verde")
            if(Hum[inver][j].values[point] < 10):
                mensajextra.append("Se debe de regar la planta 5 minutos cada hora")
            else:
                mensajextra.append("temperatura entre 6 y 32, y humedad mayor a 10")
    

    invernadero00 = create_invernadero("Invernadero "+str(inver+1)+" Cama 1",str(s_rad.values[point]), str(Temp[inver][0].values[point]),str(Hum[inver][0].values[point]),str(inver)+"_"+str(0)+"_"+str(point), str(suma) , str(suma1), mensaje[0] , mensajextra[0] )
    invernadero10 = create_invernadero("Invernadero "+str(inver+1)+" Cama 2",str(s_rad.values[point]), str(Temp[inver][1].values[point]),str(Hum[inver][1].values[point]),str(inver)+"_"+str(1)+"_"+str(point), str(suma) , str(suma1), mensaje[1] , mensajextra[1] )
    invernadero20 = create_invernadero("Invernadero "+str(inver+1)+" Cama 3",str(s_rad.values[point]), str(Temp[inver][2].values[point]),str(Hum[inver][2].values[point]),str(inver)+"_"+str(2)+"_"+str(point), str(suma) , str(suma1), mensaje[2] , mensajextra[2] )
    invernadero30 = create_invernadero("Invernadero "+str(inver+1)+" Cama 4",str(s_rad.values[point]), str(Temp[inver][3].values[point]),str(Hum[inver][3].values[point]),str(inver)+"_"+str(3)+"_"+str(point), str(suma) , str(suma1), mensaje[3] , mensajextra[3] )
    invernadero40 = create_invernadero("Invernadero "+str(inver+1)+" Cama 5",str(s_rad.values[point]), str(Temp[inver][4].values[point]),str(Hum[inver][4].values[point]),str(inver)+"_"+str(4)+"_"+str(point), str(suma) , str(suma1), mensaje[4] , mensajextra[4] )
    invernadero50 = create_invernadero("Invernadero "+str(inver+1)+" Cama 6",str(s_rad.values[point]), str(Temp[inver][5].values[point]),str(Hum[inver][5].values[point]),str(inver)+"_"+str(5)+"_"+str(point), str(suma) , str(suma1), mensaje[5] , mensajextra[5] )
    invernadero60 = create_invernadero("Invernadero "+str(inver+1)+" Cama 7",str(s_rad.values[point]), str(Temp[inver][6].values[point]),str(Hum[inver][6].values[point]),str(inver)+"_"+str(6)+"_"+str(point), str(suma) , str(suma1), mensaje[6] , mensajextra[6] )
    invernadero70 = create_invernadero("Invernadero "+str(inver+1)+" Cama 8",str(s_rad.values[point]), str(Temp[inver][7].values[point]),str(Hum[inver][7].values[point]),str(inver)+"_"+str(7)+"_"+str(point), str(suma) , str(suma1), mensaje[7] , mensajextra[7] )
    invernadero80 = create_invernadero("Invernadero "+str(inver+1)+" Cama 9",str(s_rad.values[point]), str(Temp[inver][8].values[point]),str(Hum[inver][8].values[point]),str(inver)+"_"+str(8)+"_"+str(point), str(suma) , str(suma1), mensaje[8] , mensajextra[8] )
    invernadero90 = create_invernadero("Invernadero "+str(inver+1)+" Cama 10",str(s_rad.values[point]), str(Temp[inver][9].values[point]),str(Hum[inver][9].values[point]),str(inver)+"_"+str(9)+"_"+str(point), str(suma) , str(suma1), mensaje[9] , mensajextra[9] )

    
    graphRow0 = dbc.Row([dbc.Col(invernadero00, width=3),
                     dbc.Col(invernadero10, width=3),
                     dbc.Col(invernadero20, width=3),
                     dbc.Col(invernadero30, width=3),
                     dbc.Col(invernadero40, width=3),
                     dbc.Col(invernadero50, width=3),
                     dbc.Col(invernadero60, width=3),
                     dbc.Col(invernadero70, width=3),
                     dbc.Col(invernadero80, width=3),
                     dbc.Col(invernadero90, width=3),
                     ], className = "mb-4",)
    return graphRow0

@app.callback(Output('timeseries', 'figure'), [Input('varselector', 'value'),
                                               Input('camSelector','value'),
                                               Input('my_daq_slider_ex', 'value'), 
                                               Input('demo_dropdown', 'value')])
def update_graph(varselector,camSelector,my_daq_slider_ex,demo_dropdown):
    trace1=[]
    inver = int(demo_dropdown)
    fechaSelected = '2020-04-01' 
    if (my_daq_slider_ex == 0):
        fechaSelected = '2020-03-26' 
    elif (my_daq_slider_ex == 1):
        fechaSelected = '2020-03-27' 
    elif (my_daq_slider_ex == 2):
        fechaSelected = '2020-03-28' 
    elif (my_daq_slider_ex == 3):
        fechaSelected = '2020-03-29' 
    elif (my_daq_slider_ex == 4):
        fechaSelected = '2020-03-30' 
    elif (my_daq_slider_ex == 5):
        fechaSelected = '2020-03-31' 
    elif (my_daq_slider_ex == 6):
        fechaSelected = '2020-04-01' 
    elif (my_daq_slider_ex == 7):
        fechaSelected = '2020-04-01' 

    point = -1
    for x in range(len(Temp[0][0].sensorTime)):
        if (Temp[0][0].sensorTime[x].split()[0] == fechaSelected):
            point = x

    if (varselector == 'temperatura'):
        trace1.append(go.Scatter(x=list(range(1,len(Temp[inver][camSelector].values))),y=Temp[inver][camSelector].values,mode='lines',opacity=0.7,name='grafica',textposition='bottom center'))
    elif (varselector == 'humedad'):
        trace1.append(go.Scatter(x=list(range(1,len(Hum[inver][camSelector].values))),y=Hum[inver][camSelector].values,mode='lines',opacity=0.7,name='grafica',textposition='bottom center'))
    elif (varselector == 'radiacion'):
        trace1.append(go.Scatter(x=list(range(1,len(s_rad.values))),y=s_rad.values,mode='lines',opacity=0.7,name='grafica',textposition='bottom center'))
    traces = [trace1]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data,
              'layout': go.Layout(
                  hovermode='x',
                  autosize=True,
                  title={'text': varselector},

              ),

              }
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
