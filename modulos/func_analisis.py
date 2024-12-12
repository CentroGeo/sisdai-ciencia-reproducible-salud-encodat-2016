'''
Este archivo contiene las funciones necesarias para realizar el análisis de los datos, es decir,
la aplicación de técnicas estadísticas para generar los resultados de la encuesta.
'''
import os
import numpy as np
import pandas as pd
import json

from statistics import NormalDist
from samplics.estimation import TaylorEstimator
from samplics.utils.types import SinglePSUEst

# - # - # - # - # - # ----------------- PROCESAMIENTO DE DATOS ----------------- # - # - # - # - # - # 

# ------------------ Función para calcular prevalencia en una sola variable ------------------ #
def proporciones(b, clave_preg, alp = 0.95, ponderador = 'factor_exp', estrato = 'estrato', upm = 'upm'):
    """ 
    Estima las respuestas de la población a "clave_preg".
    
    Mediante las respuestas capturadas en la base "b" se generan:
    estimaciones puntuales, su respectivo intervalo de confianza con un nivel de significancia "alp", 
    el coeficiente de variación y el error estándar. 
    
    Las estimaciones se calculan como porcentajes.

    Parámetros:
    ------------
    b : DataFrame
        Conjunto de datos.
    clave_preg : str
        Clave de la pregunta para la que se desea la estimar las proporciones.
    alp: float
        Valor entre 0 y 1 para definir el nivel de significancia del intervalo.
        El valor predeterminado es 0.95, para tener intervalos con un 95% de significancia.
    ponderador : str
        Nombre de la columna con el ponderador de la encuesta.
        El valor predeterminado es "factor_exp".
    estrato : str
        Nombre de la columna con los estratos de la encuesta. 
        Es necesario que las claves para identificar los estratos estén en formato numérico.
        El valor predeterminado es "estrato".
    upm : str
        Nombre de la columna con las unidades primarias de la encuesta.
        Es necesario que las claves para identificar las unidades primarias de muestreo estén en formato numérico.
        El valor predeterminado es "upm".
    
    Regresa:
    ------------
    DataFrame
        Tabla con la estimación puntual, intervalo de confianza, coeficiente de variación y error estándar.
    """

    # creación del objeto
    c = TaylorEstimator("proportion")
    # estimacion puntual, coeficiente de variación y error estándar.
    c.estimate(y = b[clave_preg], samp_weight = b[ponderador], stratum = b[estrato], psu = b[upm], remove_nan = False, single_psu=SinglePSUEst.skip) #REVISAR opciones: [.error, .skip, .certainty, .combine]
    
    # estructuración del dataframe
    e = c.to_dataframe()
    e.columns = [x.replace('_','') for x in list(e.columns)]
    e.rename(columns = {'level':'clave_respuesta','estimate':'estimacion', 'stderror':'error_std'}, inplace=True)
    
    # parche que soluciona que no aparezca el valor de la pregunta cuando todas las respuestas son iguales
    if len(e)==1 and e.clave_respuesta.isna().all():
        e.clave_respuesta=list(set(b[clave_preg]))

    # función cuantil para determinar coef por el que se multiplica el error estándar
    z = NormalDist().inv_cdf((1 + alp) / 2)
    # cálculo de los extremos inferior y superior del intervalo de confianza 
    e.insert(2,'ic_inf',e['estimacion']-z*e['error_std'])
    e.insert(3,'ic_sup',e['estimacion']+z*e['error_std'])
    # casos especiales en los que los intervalos no tienen sentido dentro del porcentaje 
    e.loc[e['ic_inf']<0,'ic_inf']=0
    e.loc[e['ic_sup']>100,'ic_sup']=100
    
    # estimación de la población
    g = b.groupby(clave_preg)[ponderador].sum()
    gg = pd.DataFrame(g).reset_index()
    gg.rename(columns = {clave_preg:'clave_respuesta',ponderador:'poblacion'}, inplace=True)
    
    # número de encuestas
    gg.insert(0,'num_encuestas',len(b))
    
    # estructuracion de df de salida
    ef = e.merge(gg,on = 'clave_respuesta',how = 'outer')
    ef[['estimacion','error_std','ic_inf','ic_sup','cv']] = ef[['estimacion','error_std','ic_inf','ic_sup','cv']]*100
    
    ef = ef[['clave_respuesta','estimacion','ic_inf','ic_sup','poblacion','error_std','cv']]
    
    return ef

# --------- Función para calcular prevalencia en una sola variable para distintos subconjuntos de la muestra ----------- #
def proporciones_des(b, clave_preg, var_des, alp = 0.95, ponderador = 'factor_exp', estrato = 'estrato', upm = 'upm'):
    """ 
    Estima las respuestas a "clave_preg" de la población desagregada de acuerdo a la variable "var_des".
    
    Mediante las respuestas capturadas en la base "b" se generan:
    estimaciones puntuales, su respectivo intervalo de confianza con un nivel de significancia "alp", 
    el coeficiente de variación y el error estándar. 
    
    Las estimaciones se calculan como porcentajes.

    Parámetros:
    ------------
    clave_preg : str
        Clave de la pregunta para la que se desea la estimar las proporciones
    b : DataFrame
        Conjunto de datos.
    var_des: list
        Lista con las variable(s) en las que se desea desagregar la base b.
    alp: float
        Valor entre 0 y 1 para definir el nivel de significancia del intervalo.
        El valor predeterminado es 0.95, para tener intervalos con un 95% de significancia.
    ponderador : str
        Nombre de la columna con el ponderador de la encuesta.
    estrato : str
        Nombre de la columna con los estratos de la encuesta.
        Es necesario que las claves estén en formato numérico.
    upm : str
        Nombre de la columna con las unidades primarias de la encuesta.
        Es necesario que las claves estén en formato numérico.
    
    Regresa:
    ------------
    DataFrame
        Tabla con las estimaciones puntuales y sus respectivos intervalos de confianza, coeficiente de variación y error. estándar.
    """
    res={}
    # división de la base de datos en subconjuntos de acuerdo a la variable "var_des"
    b_gb=b.groupby(var_des,sort=False)
    
    # estimación calculada para cada subconjunto de la muestra 
    for ks, b_red in b_gb:
        res[ks] = proporciones(b_red, clave_preg, alp, ponderador, estrato, upm).set_index('estimacion')
    
    # estructuración del dataframe de salida
    resultado = pd.concat(res).reset_index()
    resultado.rename(columns=dict(zip(list(resultado.columns[0:len(var_des)]),var_des)), inplace=True)

    return resultado.sort_values(var_des)

# --------------- Función para calcular prevelencia de una variable o más ---------------- #
def prevalencias(b, lista_vars, dicc, alp = 0.95, ponderador = 'factor_exp', estrato = 'estrato', upm = 'upm'):
    """
    Estima el porcentaje de personas a las que les ha ocurrido al menos uno de los eventos en la lista de variables "lista_vars".
    Las estimaciones se calculan como porcentajes.
    
    Funcionamiento
    --------------
    Mediante el diccionario 'dicc', la función recategoriza las respuestas a las preguntas de la lista de variables 'lista_vars' de la siguiente manera: 
    1 si el evento ocurrió
    0 si el evento no ocurrió
    Posteriormente suma las respuestas recategorizadas, de modo que si en alguna de las preguntas ocurrió el evento, la suma será positiva. 
    Mientras que la magnitud del número entero describe la cantidad de ocurrencias del evento.
    
    Parámetros
    ----------
    b : DataFrame
        Conjunto de datos.
    lista_vars : lista
        Lista con los nombres de las variables para las que se desea calcular prevalencia.
    dicc : diccionario
        Diccionario con las claves de las preguntas renombradas respectivamente como 0 y 1.
    alp: float
        Valor entre 0 y 1 para definir el nivel de significancia del intervalo.
        El valor predeterminado es 0.95, para tener intervalos con un 95% de significancia.
    ponderador : str
        Nombre de la variable que contiene el ponderador.
    estrato : str
        Nombre de la columna con los estratos de la encuesta.
        Es necesario que las claves estén en formato numérico.
    upm : str
        Nombre de la columna con las unidades primarias de la encuesta.
        Es necesario que las claves estén en formato numérico.

    Salida
    ------
    DataFrame
        Tabla con la estimación puntual para la ocurrencia, su intervalo de confianza, coeficiente de variación y error estándar.
    """
    
    listaT = lista_vars + [ponderador, estrato, upm]
    
    # condicionales para garantizar que el diccionario que utiliza la función está bien hecho
    rv=[set(b[x].dropna()) for x in lista_vars]
    # criterio para revisar que todas las posibles respuestas de 'lista_vars' están en 'dicc'
    c1=set.union(*rv)-(set(dicc.keys()).union({1,0}))
    # criterio para revisar que todas las posibles respuestas se clasifican como 0s o 1s
    c2=set(dicc.values())
    
    if c1==set({}) and c2.issubset({0,1}):
        # cálculo de frecuencia con la que ocurrió el evento en una copia reducida del conjunto de datos originales.
        b_red = b[listaT]
        b_red.insert(0, 'var_agrupada_frec', b_red[lista_vars].replace(dicc).sum(axis=1))
        # creación de la variable que indica si hubo ocurrencia del evento.
        b_red.insert(0, 'var_agrupada', 0)
        b_red.loc[b_red['var_agrupada_frec']>0,'var_agrupada'] = 1

        # estimación para la variable que indica ocurrencia.
        pcj = proporciones(b_red, 'var_agrupada', alp, ponderador, estrato, upm)

        # correción para los casos en que sólo hay un tipo de respuesta
        if len(pcj)==1:
            #inclusión de nuevo renglón llenado con ceros en variables que sabemos que serán cero
            porcentajes = pd.concat([pcj,pd.DataFrame({'poblacion':[0],'error_std':[0],'cv':[0]}, index=[1])])
            #llenado manual de valores distintos de cero
            porcentajes.at[1,'clave_respuesta']=1-porcentajes.loc[0,'clave_respuesta']
            porcentajes.at[1,'estimacion']=100-porcentajes.loc[0,'estimacion']
            porcentajes.at[1,'ic_inf']=porcentajes.loc[1,'estimacion']
            porcentajes.at[1,'ic_sup']=porcentajes.loc[1,'estimacion']
           
        else:
            porcentajes = pcj

        # estructuración del dataframe de salida
        ocurrencia = porcentajes[porcentajes['clave_respuesta']==1]
    
    else:
        # criterio para revisar que todas las posibles respuestas de 'lista_vars' están en 'dicc'
        if c1!=set({}):
            raise AssertionError("En el diccionario para reclasificar falta incluir la(s) clave(s): "+str(c1).replace('{','').replace('}',''))
    
        # criterio para revisar que todas las posibles respuestas se clasifican como 0s o 1s
        elif c2.issubset({0,1})==False:
            raise AssertionError(
                "Los valores para reclasificar sólo pueden ser 1 o 0")
            
    ocurrencia = ocurrencia[['estimacion','ic_inf','ic_sup','poblacion','error_std','cv']]
    
    return ocurrencia

# --------- Función para calcular prevelencias desagregadas por otra variable -------- #
def prevalencias_des(b, lista_vars, dicc, var_des, alp = 0.95, ponderador = 'factor_exp', estrato = 'estrato', upm = 'upm'):
    """
    Desagrega la población de acuerdo a la variable "var_des" y posteriormente estima a qué porcentaje de cada subconjunto le ha ocurrido al menos uno de los eventos en la lista de variables "lista_vars".
    Las estimaciones se calculan como porcentajes.
    
    Parámetros
    ----------
    b: DataFrame
        Conjunto de datos.
    lista_vars: lista
        Lista con los nombres de las variables para las que se desea calcular prevalencia.
    var_des: list
        Lista con las variable(s) en las que se desea desagregar la base b.
    dicc: diccionario
        Diccionario con las claves de las preguntas renombradas respectivamente como 0 y 1.
    alp: float
        Valor entre 0 y 1 para definir el nivel de significancia del intervalo.
        El valor predeterminado es 0.95, para tener intervalos con un 95% de significancia.
    ponderador: str
        Nombre de la variable que contiene el ponderador.
    estrato : str
        Nombre de la columna con los estratos de la encuesta.
        Es necesario que las claves estén en formato numérico.
    upm : str
        Nombre de la columna con las unidades primarias de la encuesta.
        Es necesario que las claves estén en formato numérico.
        
    Salida
    ------
    DataFrame
        Tabla con la estimación puntual para la ocurrencia, su intervalo de confianza, coeficiente de variación y error estándar.
    """
    
    # división de la base de datos en subconjuntos de acuerdo a la variable "var_des"
    res={}
    b_gb=b.groupby(var_des,sort=False)
    
    # estimación calculada para cada subconjunto de la muestra
    for ks, b_red in b_gb:
        res[ks] = prevalencias(b_red, lista_vars, dicc, alp, ponderador, estrato, upm).set_index('estimacion')

    # estructuración del dataframe de salida
    resultado = pd.concat(res).reset_index()
    resultado.rename(columns=dict(zip(list(resultado.columns[0:len(var_des)]),var_des)), inplace=True)

    return resultado.sort_values(var_des)

# --- Función para agupar los cálculos de prevelencias totales y desagregadas por sexo y grupo etario --- #
def tabulados_prevalencias(b, lista_vars, dicc, var_des = [], alp = 0.95, var_ge='grupo_etario', ponderador = 'factor_exp', estrato = 'estrato', upm = 'upm'):
    """
    Estructura un dataframe con las prevalencias de lista_vars, totales y desagregadas por sexo y grupo etario.
    
    Parámetros
    ----------
    b: DataFrame
        Conjunto de datos.
    lista_vars: lista
        Lista con los nombres de las variables para las que se desea calcular prevalencia.
    dicc: diccionario
        Diccionario con las claves de las preguntas renombradas respectivamente como 0 y 1.
    var_des: list
        Lista con las variable(s) en las que se desea desagregar la base b.
    alp: float
        Valor entre 0 y 1 para definir el nivel de significancia del intervalo.
        El valor predeterminado es 0.95, para tener intervalos con un 95% de significancia.
    ponderador: str
        Nombre de la variable que contiene el ponderador.
    estrato : str
        Nombre de la columna con los estratos de la encuesta.
        Es necesario que las claves estén en formato numérico.
    upm : str
        Nombre de la columna con las unidades primarias de la encuesta.
        Es necesario que las claves estén en formato numérico.
        
    Salida
    ------
    DataFrame
        Tabla agrupando las estimaciones por sexo y grupo etario de acuerdo a la desagregación var_des (si es que se incluyó).
    """
    # estimación de prevalencia para toda la población desagregada por sexo y grupo etario
    x2 = prevalencias_des(b, lista_vars, dicc, var_des + ['sexo',var_ge], alp, ponderador, estrato, upm)
    
    # estimación de prevalencia para toda la población desagregada por sexo
    x1 = prevalencias_des(b, lista_vars, dicc, var_des + ['sexo'], alp, ponderador, estrato, upm)
    x1.insert(0,var_ge,'Población de 12-75 años')
    
    # estimación de prevalencia para toda la población
    if var_des == []:       
        x0 = prevalencias(b, lista_vars, dicc, alp, ponderador, estrato, upm)
    else: 
        x0 = prevalencias_des(b, lista_vars, dicc, var_des, alp, ponderador, estrato, upm)
    
    x0.insert(0,var_ge,'Población de 12-75 años')
    x0.insert(0,'sexo', 'Mujeres y hombres')
    
    #agrupado de las distintas estimaciones
    x=pd.concat([x0,x1,x2]).rename(columns={var_ge:'grupo_etario'})
    
    return x
