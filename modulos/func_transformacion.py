'''
Este archivo contiene las funciones para estructurar datos, preparándolos para el análisis. 
Esto incluye la limpieza de los datos, la identificación y corrección de errores de origen, 
manejo de valores faltantes e imputación de los datos. También abarca tareas como la integración 
de códigos geográficos y la limpieza de valores de cadena, entre otros.
'''
import os
import numpy as np
import pandas as pd
import warnings
import json
warnings.filterwarnings('ignore')

# ---- # ---- #  FUNCIONES PARA LIMPIEZA Y ESTRUCTURACIÓN DE DATOS  # ---- # ---- #   

# ------------------ Función para procesar códigos geográficos ------------------ #
def procesar_datos_geo(b, vars_str, var_ent, var_mun, var_loc):
    """
    Genera un procesamiento para limpiar los datos geográficos de la encuesta ENCODAT 2016.

    Parámetros
    ----------
    b : str
        Nombre del archivo con los datos geográficos de la encuesta ENCODAT 2016.
    vars_str : list
        Lista con las variables que son de tipo string.
    var_ent : str
        Nombre de la variable con la clave de la entidad.
    var_mun : str
        Nombre de la variable con la clave del municipio.
    var_loc : str
        Nombre de la variable con la clave de la localidad.

    Regresa
    -------
    DataFrame
        Un dataframe con los datos geográficos limpios.
    """

    b = b.astype({str(var):str for var in vars_str})

    b[var_ent] = b[var_ent].apply(lambda x: format(x, '.0f')).astype(str).str.zfill(2)
    b[var_mun] = b[var_mun].apply(lambda x: format(x, '.0f')).astype(str).str.zfill(3)
    b[var_loc] = b[var_loc].apply(lambda x: format(x, '.0f')).astype(str).str.zfill(4)

    # eliminado de las claves geo en la variable con el nombre del lugar
    #b['desc_ent'] = b['desc_ent'].str.replace('^[0-9]+', '', regex=True)
    #b['desc_mun_sn'] = b['desc_mun'].str.replace('^[0-9]+', '', regex=True)
    #b['desc_loc_sn'] = b['desc_loc'].str.replace('^[0-9]+', '', regex=True)

    # generación de claves geoestadísticas
    b['cvegeomun'] = b[var_ent] + b[var_mun]
    b['cvegeoloc'] = b[var_ent] + b[var_mun] + b[var_loc]

    return b

# --------- Genera diccionarios de variables geográficas --------- #
def generar_diccs_geo(b, val_geo, etiqueta_geo):
    """ 
    Genera un archivo json con los datos de estados, municipios, localidades de acuerdon a la referencia del conjunto de datos de entrada.

    Parámetros:
    -----------
    b: df
        Conjunto de datos de entrada.
    val_geo: str
        Nombre de la columna con los valores de la variable geográfica.
    etiqueta_geo: str
        Nombre de la columna con la etiqueta de la variable geográfica.
    
    Regresa:
    -------
        Json con los datos de la variable geográfica.
    """

    dicc_geo = dict(zip(b[val_geo].unique(), b[etiqueta_geo].unique()))
    ruta = os.path.join('..', '..', 'datos', 'datos_auxiliares', 'dicc_' + val_geo + '_16.json')
    with open(ruta, 'w') as fp:
        json.dump(dicc_geo, fp, indent=4, ensure_ascii = False)

# ------------------ Función para homologar variables numéricas a flotantes ------------------ #
### incluir parámetro de ¿cols_homologar?
def obj_a_num(b,l_nulos,l_excep=[]):
    """Convierte las columnas de tipo object a tipo numérico.

        Para ello inicia reemplazando el listado de strings que definen un dato nulo por Na,
        posteriormente detecta las columnas que son de tipo objeto y sobre éstas itera
        para cambiar -en los casos en que es posible- los tipos de datos a numéricos.

        Parámetros
        ----------
        b : DataFrame
            Conjunto de datos para el cual se desea homologar los tipos de variables.
        l_nulos : list
            Lista con strings que definen un dato nulo
        l_excep : list
            Lista con nombres de las columnas que se desean excluir de la homologación a tipo numérico.

        Salida
        ------
        DataFrame
            Un dataframe con datos numéricos en los casos en que fue posible.
    """
    
    # reemplazo de valores vacíos por Na para que se reeconozcan los tipos numéricos
    for n in l_nulos:
        b.replace(n,pd.NA, inplace = True)
        
    # identificación de las columnas con tipo de variable objeto
    #¿tal vez aqui generalizar a cualquier columna y que forzosamente debamos especificar que columnas no incluir?
    oo = b.select_dtypes(include = 'object').columns
    if l_excep!=[]:
        ob=list(set(oo).difference(set(l_excep)))
    else:
        ob=oo
    # nueva base con tipos de datos cambiados
    nb = b
    
    # cambio del tipo de variables objeto a flotante cuando se puede
    print('Inicia homologación, esto puede tardar unos minutos')
    print('...')
    for c in ob:
        nb[c] = pd.to_numeric(b[c], downcast = 'integer', errors = 'ignore')
    print('Homologación terminada.')
    print('')
    print('La base original tenía:')
    print(str(len(ob))+" columnas de tipo objeto.")
    print("")
    
    obn = nb.select_dtypes(include = 'object').columns
    enn = nb.select_dtypes(include = 'integer').columns
    fln = nb.select_dtypes(include = 'float').columns
    print('Después de aplicar la función, la nueva base tiene:')
    print(str(len(obn))+" columnas de tipo objeto")
    print(str(len(enn))+" columnas de tipo entero")
    print(str(len(fln))+" columnas de tipo flotante.")
    
    return nb

# --------------------- Corrección de palabras --------------------- #
def arreglar_palabras(s):
    """ 
    Corrige los artículos que no deberían estar en mayúsculas.
    """
    articulos = ['en', 'la', 'los', 'de', 'el', 'y', 'las', 'de', 'lo']
    palabras = s.split()
    for i, palabra in enumerate(palabras):
        if palabra.lower() not in articulos:
            palabras[i] = palabra.capitalize()
        else:
            palabras[i] = palabra.lower()
    return ' '.join(palabras)

# ------------------ Función para generar grupos etarios ------------------ #
def grupo_etario(b, var_edad, gps=['12-17', '18-34', '35-59', '60-75'], nom_ge='grupo_etario'):
    """
    Genera una nueva variable llamada "grupo_etario" donde se agrupan las edades de acuerdo a

    Parámetros:
    -----------
    b : Dataframe
        base de datos
    var_edad :  str        
        nombre de la variable con las edades
    gps : list
        lista de strings describiendo los grupos etarios que se desean.
    
    Regresa:
    --------
    DataFrame
        conjunto de datos "b" con la variable grupo_etario.
    """
    # creación de lista con intervalos para categorizar las edades
    divisiones=[int(x[:2])-1 for x in gps]+[int(gps[-1][-2:])]
    etiquetas=[g+' años' for g in gps]
    # dataframe de salida
    b.insert(len(b.columns),nom_ge,pd.cut(list(b['ci1']), bins=divisiones, labels=etiquetas))
    return b