'''
Este archivo contiene las funciones necesarias para desarrollar gráficos y visualizaciones, 
los cuales facilitan la comunicación visual de los hallazgos obtenidos a partir de los datos analizados.
'''
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# - # - # - # - # - # ----------------- VISUALIZACIÓN DE DATOS ----------------- # - # - # - # - # - # 

# ------------------ Función que genera gráfico de dispersión con tabla ------------------ #
def grafico_dispersion(tabulado, ruta, extension = '.csv', ruta_salida = ('..','..','informe-preliminar','salidas-graficas')):
    p = os.path.join( *(ruta + (tabulado+extension,)))
    if extension == '.csv':
        b0 = pd.read_csv(p)
    elif extension == '.xlsx':
        b0 = pd.read_excel(p)
    else:
        print('solo se aceptan archivos en csv o xlsx')

    b= b0[b0['sexo']=='Mujeres y hombres']
    b.insert(0,'e_sup',(b['ic_sup']-b['estimacion']).round(2))
    b.insert(0,'e_inf',(b['estimacion']-b['ic_inf']).round(2))
    b.loc[:,'estimacion']=b['estimacion'].round(2)

    fig = make_subplots(
        rows=1, cols=2,
        horizontal_spacing=0.01,
        specs=[[{"type": "scatter"},
               {"type": "table"}]])

    fig.add_trace(
        go.Table(columnwidth = [300,200,200],
                 header=dict(values=['Entidad','Estimación','Error'],
                             align='left',
                             fill_color='white',
                             font=dict(size=14)),
                 cells=dict(values=[b['entidad'],b['estimacion'],b['e_sup']], 
                            align='left',
                            fill_color='white')),
        row=1, col=2
    )

    fig.add_trace(
        go.Scatter(x=b["estimacion"], 
                   y=34-b["clave_entidad_dai"], 
                   mode='markers', 
                   marker=dict(
                       color='#002663',
                       size=8),
                   error_x=dict(type='data', symmetric=False, array=list(b["e_sup"]), arrayminus=list(b["e_inf"]))),
        row=1, col=1
    )

    fig.update_layout(
        height=880,
        width=900,
        showlegend=False,
        title= dict(text='', x=0.18, xanchor='center', y=0.92, yanchor='bottom', font=dict(size=24)),
        xaxis_title = dict(text='Porcentaje con respecto al total de personas encuestadas'),
        xaxis={'side': 'right'},
        plot_bgcolor='white'
    )
    fig.update_yaxes(showline=True, linecolor='lightgray', nticks=60, gridwidth=1, griddash='dot', gridcolor='lightgray', showticklabels=False)
    fig.update_xaxes(zeroline=True, zerolinecolor='lightgray',zerolinewidth=1, showline=True, linecolor='lightgray', mirror=True, gridcolor='lightgray')

    fig.show()
    #ruta_salida = ('..','..','informe-preliminar','salidas-graficas')
    fig.write_image(os.path.join( *(ruta_salida + (tabulado+'.png',))))
    
    
# ------------------ Función que genera gráfico de barras desagregadas por sexo ------------------ #
def barras_sexo(b, categorias, orden_cat, nombre_salida, espaciado=' '*10, aumento_rango=3):
    """ 
    Genera gráfico de barras mostrando estimaciones agrupadas de acuerdo 
    a la variable "categorias" y desglosadas por sexo.

    Parámetros:
    ------------
    b : DataFrame
        Conjunto de datos.
    categorias : str
        Variable en la que se agrupan las barras.
    orden_cat: list
        Lista con el orden en el que se desea que aparezcan las categorías.
    nombre_salida : str
        Nombre de la archivo donde se guardará la imagen del gráfico.
    espaciado: str
        Espacios en blanco entre la barra y el valor de la barra.
        El valor predeterminado es ' '*10.
    aumento_rango: int
        Longitud que se aumentará del rango.
        El valor predeterminado es 3
    
    Regresa:
    ------------
    archivo
        archivo con la imagen del gráfico.
    """
    #constantes
    max_v= b.estimacion.max() + (b.e_sup.max()*aumento_rango)
    colores_hym = {'Mujeres':'#714859', 'Hombres': '#b38e5d'}

    if orden_cat==[]:
        b=b.sort_values('estimacion')
    
    pio.templates.default = "simple_white"
    
    fig = go.Figure()
    for g,c in b.groupby('sexo'):
        fig.add_trace(go.Bar(x=c['estimacion'],
                             y=c[categorias],
                             orientation='h',
                             name=g,
                             marker_color=colores_hym[g],
                             text=[espaciado+str(x) for x in c['estimacion']],
                             error_x=dict(type='data',
                                          symmetric=False,
                                          array=list(c["e_sup"]),
                                          arrayminus=list(c["e_inf"])),
                            )
                     )

    #especificaciones del grafico
    fig.update_layout(height=500,
                      width=1000,
                      paper_bgcolor ='rgba(0, 0, 0, 0)',
                      font = dict(
                               family = 'Montserrat',
                               size = 16,
                               color="dark gray" 
                      ),
                      barmode='group',
                      bargroupgap=0.0,
                      bargap=0.15,
                     )

    #para nombrar eje
    fig.add_annotation(text='Porcentaje de las personas encuestadas',
                       xref="paper", 
                       yref="paper",
                       x=0.5, y=-0.15, 
                       showarrow=False)
    
    fig.update_xaxes(linecolor='lightgray', tickcolor='darkgray',  autorangeoptions_include=max_v,
                    )
    if orden_cat!=[]:
        fig.update_yaxes(linecolor='lightgray', categoryorder='array', categoryarray= orden_cat, ticks='')
    else:
        fig.update_yaxes(linecolor='lightgray', categoryorder='array', ticks='')

    fig.update_traces(textposition = "outside")
    fig.update_annotations(font_size=16)
    
    #para que muestre etiquetas una única vez
    fig.write_image(os.path.join('salidas-graficas',nombre_salida+'.png'), scale=3)
    

# ------------------ Función que genera gráfico de barras desagregadas por temporalidad ------------------ #    
def barras_temporalidad(b, categorias, nombre_salida, espaciado=' '*10, aumento_rango=3):
    """ 
    Genera una retícula con gráficos de barras mostrando estimaciones desglosadas por la variable "var_barras". 

    Parámetros:
    ------------
    b : DataFrame
        Conjunto de datos.
    categorias : str
        Variable en la que se agrupan las barras.
    nombre_salida : str
        Nombre de la archivo donde se guardará la imagen del gráfico.
    espaciado: str
        Espacios en blanco entre la barra y el valor de la barra.
        El valor predeterminado es ' '*10.
    aumento_rango: int
        Longitud que se aumentará del rango.
        El valor predeterminado es 3
    
    Regresa:
    ------------
    archivo
        archivo con la imagen del gráfico.
    """
    #constantes
    max_v= b.estimacion.max() + (b.e_sup.max()*aumento_rango)
    colores_hym = dict(zip(list(set(b.temporalidad)),['#285c4d','#d4c19c']))#{'Último año':'#285c4d','Consumo actual':'#d4c19c'}#{'Último año':'#285c4d', 'Último mes':'#d4c19c'}#

    
    pio.templates.default = "simple_white"
    
    fig = go.Figure()
    for g,c in b.groupby('temporalidad'):
        fig.add_trace(go.Bar(x=c['estimacion'],
                             y=c[categorias],
                             orientation='h',
                             name=g,
                             marker_color=colores_hym[g],
                             text=[espaciado+str(x) for x in c['estimacion']],
                             error_x=dict(type='data',
                                          symmetric=False,
                                          array=list(c["e_sup"]),
                                          arrayminus=list(c["e_inf"])),
                            )
                     )

    #especificaciones del grafico
    fig.update_layout(height=500,
                      width=1000,
                      paper_bgcolor ='rgba(0, 0, 0, 0)',
                      font = dict(
                               family = 'Montserrat',
                               size = 16,
                               color="dark gray" 
                      ),
                      barmode='group',
                      bargroupgap=0.0,
                      bargap=0.15,
                     )

    #para nombrar eje
    fig.add_annotation(text='Porcentaje de las personas encuestadas',
                       xref="paper", 
                       yref="paper",
                       x=0.5, y=-0.15, 
                       showarrow=False)
    
    fig.update_xaxes(linecolor='lightgray', tickcolor='darkgray',  autorangeoptions_include=max_v,
                    )
    fig.update_yaxes(linecolor='lightgray', ticks='') #categoryorder='array', categoryarray= orden_cat,
    fig.update_traces(textposition = "outside")
    fig.update_annotations(font_size=16)
    
    #para que muestre etiquetas una única vez
    fig.write_image(os.path.join('salidas-graficas',nombre_salida+'.png'), scale=3)
    


# ------------------ Función que genera renglón de gráficos de barras ------------------ # 
def barras_renglon(b, var_cols, categorias, orden_cat, orden_cols, nombre_salida, espaciado=' '*10, aumento_rango=3):
    """ 
    Genera columnas con gráficos de barras mostrando estimaciones agrupadas de acuerdo 
    a la variable "categorias" y desglosadas por sexo.

    Parámetros:
    ------------
    b : DataFrame
        Conjunto de datos.
    var_cols : str
        Variable que define el subconjunto de datos que genera el gráfico por columna.
    categorias : str
        Variable en la que se agrupan las barras.
    orden_cat: list
        Lista con el orden en el que se desea que aparezcan las categorías.
    orden_cols: list
        Lista con el orden en que se desea que aparezcan las categorías que definen las columnas.
    nombre_salida : str
        Nombre de la archivo donde se guardará la imagen del gráfico.
    espaciado: str
        Espacios en blanco entre la barra y el valor de la barra.
        El valor predeterminado es ' '*10.
    aumento_rango: int
        Longitud que se aumentará del rango.
        El valor predeterminado es 3
    
    Regresa:
    ------------
    archivo
        archivo con la imagen del gráfico.
    """
    #constantes
    colores_hym = {'Mujeres':'#714859', 'Hombres': '#b38e5d'}
    nr = 1
    nc = len(set(b[var_cols]))
    max_v= b.estimacion.max() + (b.e_sup.max()*6)
    
    #preprocesamiento para graficar
    agrupado = b.groupby(var_cols)

    #especificaciones de forma de grafica
    pio.templates.default = "simple_white"
    fig = make_subplots(
        rows=1, 
        cols=nc,
        subplot_titles=(orden_cols),
        shared_yaxes=True,
        shared_xaxes=False,
    )
    #generacion de renglones con graficas
    columna=0
    for f in orden_cols:
        columna+=1
        sb=agrupado.get_group(f)
        for g,c in sb.groupby('sexo'):
            fig.add_trace(go.Bar(x=c['estimacion'],
                                    y=c[categorias],
                                    orientation='h',
                                    name=g,
                                    marker_color=colores_hym[g],
                                    text=['  '+str(x) for x in c['estimacion']],
                                    error_x=dict(type='data',
                                                  symmetric=False,
                                                  array=list(c["e_sup"]),
                                                  arrayminus=list(c["e_inf"])),
                                ),
                          1,
                          columna
                         )

    #mas especificaciones del grafico
    fig.update_layout(height=500,
                      width=1000,
                      paper_bgcolor ='rgba(0, 0, 0, 0)',
                      font = dict(
                               family = 'Montserrat',
                               size = 14,
                               color="dark gray" 
                      ),
                      barmode='group'
                     )


    #para nombrar eje
    fig.add_annotation(text='Porcentaje de las personas encuestadas',
                       xref="paper", 
                       yref="paper",
                       x=0.5, y=-0.15, 
                       showarrow=False)
    
    fig.update_xaxes(matches='x', autorangeoptions_include=max_v, linecolor='lightgray', tickcolor='darkgray')
    for i in range(1,nc+1):
        fig.update_yaxes(col=i, linecolor='lightgray', categoryorder='array', categoryarray=orden_cat, ticks='')
    fig.update_traces(textposition = "outside")
    fig.update_annotations(font_size=14)
    
    #para que muestre etiquetas una única vez
    names = set() 
    fig.for_each_trace(lambda trace: trace.update(showlegend=False) if (trace.name in names) else names.add(trace.name))

    fig.write_image(os.path.join('salidas-graficas',nombre_salida+'.png'), scale=3)
    
    
# ------------------ Función que genera retícula de gráficos de barras ------------------ # 
def barras_reticula(b, var_cols, var_reng, var_barras, orden_gps, nombre_salida, espaciado=' '*10, aumento_rango=3):
    """ 
    Genera una retícula con gráficos de barras mostrando estimaciones desglosadas por la variable "var_barras". 

    Parámetros:
    ------------
    b : DataFrame
        Conjunto de datos.
    var_cols : str
        Variable que define el subconjunto de datos que genera el gráfico por columna.
    var_reng : str
        Variable que define el subconjunto de datos que genera el gráfico por renglón.
    var_barras: str
        Variable que en el que se desglosan los gráficos de barras.
    orden_gps: list
        Lista de parejas ordenadas que define el orden en que aparecerán las categorías de 
        var_cols y var_reng en los renglones y columnas. 
    nombre_salida : str
        Nombre de la archivo donde se guardará la imagen del gráfico.
    espaciado: str
        Espacios en blanco entre la barra y el valor de la barra.
        El valor predeterminado es ' '*10.
    aumento_rango: int
        Longitud que se aumentará del rango.
        El valor predeterminado es 3
    
    Regresa:
    ------------
    archivo
        archivo con la imagen del gráfico.
    """
    #constantes y dic de utilidad
    nr = len(set(b[var_reng]))
    nc =len(set(b[var_cols]))
    max_v = b.estimacion.max() + (b.e_sup.max()*aumento_rango)
    colores_hym = {'Mujeres':'#714859', 'Hombres': '#b38e5d'}
    
    #preprocesamiento para graficar
    agrupado = b.groupby([var_cols,var_reng])

    #especificaciones de forma de grafica
    pio.templates.default = "simple_white"
    fig = make_subplots(
        rows=nr, 
        cols=nc,
        subplot_titles=[x[0]+' - '+x[1] for x in orden_gps],
        shared_yaxes=True,
        shared_xaxes=False,
    )
    for i,gpo in enumerate(orden_gps):
        renglon=int(i%2 + 1)
        columna=int(np.ceil((i%4 + 1)/2))
        c=agrupado.get_group(gpo)
        fig.add_trace(go.Bar(x=c['estimacion'],
                             y=c[var_barras],
                             orientation='h',
                             #name=g,
                             marker_color=colores_hym[gpo[0]],
                             text=[espaciado+str(x) for x in c['estimacion']],
                             error_x=dict(type='data',symmetric=False,
                                          array=list(c["e_sup"]),
                                          arrayminus=list(c["e_inf"]))
                            ),
                      columna,
                      renglon,
                     )
        
    
    #mas especificaciones del grafico
    fig.update_layout(height=500,
                      width=1000,
                      paper_bgcolor ='rgba(0, 0, 0, 0)',
                      font = dict(
                               family = 'Montserrat',
                               size = 12,
                               color="dark gray" 
                      ),
                      barmode='group'
                     )


    #para nombrar eje
    fig.add_annotation(text='Porcentaje de las personas encuestadas',
                       xref="paper", 
                       yref="paper",
                       x=0.5, y=-0.15, 
                       showarrow=False)
    
    fig.update_xaxes(matches='x', autorangeoptions_include=max_v)
    fig.update_traces(textposition = "outside")
    fig.update_annotations(font_size=12)
    
    #para que muestre etiquetas una única vez
    categorias = set()
    fig.for_each_trace(lambda trace: trace.update(showlegend=False) if (trace.name in categorias) else categorias.add(trace.name))

    fig.write_image(os.path.join('salidas-graficas',nombre_salida+'.png'), scale=3)