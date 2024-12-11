# Procesamientos y cálculos para la Encuesta Nacional de Consumo de Drogas, Alcohol y Tabaco, ENCODAT 2016-2017. 

![Estatus](https://img.shields.io/badge/Estatus-desarrollo-yellow)

## Introducción / Acerca de este proyecto
Este repositorio es parte del movimiento de ciencia abierta, el cual busca transparentar la metodología, prácticas y resultados de los procesos de análisis de datos. En particular en este repositorio se comparten las funciones, scripts y cuadernos generados para analizar encuestas.

Como ejemplo de uso, se calcula la prevalencia en el consumo de sustancias en México y se generan tabulados con los datos de la Encuesta Nacional de Consumo de Drogas, Alcohol y Tabaco 2016-2017 (abreviada como ENCODAT 2016-2017). Sin embargo, las funciones de Python se pueden utilizar con otras bases de datos que contengan información de muestras complejas de encuestas.

## Requerimientos

Las funciones de este repositorio están hechas en Python, por ello es necesario tener instalado **Python 3.10** (o superiores) para poder ejecutar los cuadernos de trabajo.

Adicionalmente se requieren las siguientes bibliotecas:

* [pandas](https://pandas.pydata.org/)
* [openpyxl](https://openpyxl.readthedocs.io/en/stable/)
* [samplics](https://github.com/samplics-org/samplics)
* [jupyter notebook](https://jupyter.org/)

## Instalación

Para instalar las bibliotecas antes mencionadas es recomendable crear un [entorno virtual](https://docs.python.org/es/3.8/library/venv.html#venv-def). Existen distintas herramientas de instalación que te permiten crear entornos virtuales. En esta sección se dan las instrucciones para generar un entorno virtual con: pipenv y conda, sin embargo la persona usuaria puede utilizar la herramienta o manejador de entorno virual que prefiera.

#### Instrucciones
0. Descarga el repositorio.
1. Desde la terminal, entra a la carpeta donde se localiza este repositorio. En dicha carpeta crea un ambiente virtual con **Python 3.10** y actívalo de la siguiente manera:
    
    - con `pipenv`:

    ```bash
    pipenv shell --python 3.10
    ```
    - con `conda`:

    ```bash
    conda create --name nombre_del_ambiente python==3.10
    conda activate nombre_del_ambiente
    ```

2. Activa el ambiente virtual e instala `pip-tools` dentro del ambiente virtual:
    
    - con `pip`:

    ```bash
    pip install pip-tools==7.3.0
    ```
    - con `conda`:

    ```bash
    conda install -c conda-forge pip-tools
    ```

Nota: Después de este paso, podría ser necesario reiniciar la terminal, con la finalidad de que el ambiente virtual se active correctamente.

3. Genera el archivo *requirements.txt* acorde arquitectura de tu sistema operativo:

    ```bash
    pip-compile requirements.in
    ```
4. Instala las bibliotecas o dependencias:

    ```bash
    pip-sync requirements.txt
    ```

5. Puedes asegurarte que la instalación de dependencias fue exitosa ejecutando el siguiente comando:

    ```bash
    pip list
    ```
    o 
    ```bash
    conda list
    ```
    Si te aparece un listado con las bibliotecas mencionadas en la sección [Requerimientos](##Requerimientos) significa que la instalación fué exitosa. Nota: es normal que además de las bibliotecas requeridas se hayan instalado otras dependencias.

6. Una vez que hayas instalado lo necesario en tu ambiente virtual es posible ejecutar los cuadernos y funciones de este repositorio. Para ello, sigue las instrucciones de la sección [Ejecución](##Ejecución).

## Ejecución

Este repositorio muestra cómo estructurar y procesar las bases de datos de la ENCODAT para estimar el consumo de sustancias mediante el cuaderno "estimacion_consumo_sustancias".

Para ejecutar el cuaderno es necesario descargar los datos de la encuesta ([disponibles en este enlace](https://encuestas.insp.mx/repositorio/encuestas/ENCODAT2016/)) y colocarlos en la carpeta "datos/originales/". Posteriormente se ejecuta cada una de las celdas del cuaderno, si todas las celdas se ejecutan correctamente, se generan seis archivos separados por comas (csv) con los resultados de las estimaciones hechas a partir de las preguntas relativas al consumo de alcohol, drogas y tabaco.

Ahora bien,  el procesamiento y estructuración de las bases de datos se hacen mediante las funciones en los módulos func_analisis y func_transformación. Las funciones son lo suficientemente generales como para poder hacer estimaciones de cualquiera de las preguntas en la encuesta, basta cambiar la clave de pregunta, definir el nivel de desagregación en el que se quieren generar las estimaciones y definir cómo se van a interpretar las claves de respuesta de la pregunta seleccionada. En el cuaderno "estimacion_general" se ejemplifica cómo se puede hacer una estimación de una pregunta arbitraria.


## Licencia

**SOFTWARE LIBRE Y ESTÁNDARES ABIERTOS**

Este proyecto se encuentra alineado al Sisdai que a su vez, parte de las disposiciones establecidas por la Coordinación de Estrategia Digital Nacional (DOF:06/09/2021) en donde se estipula que las "políticas y disposiciones tienen como objetivo fortalecer el uso del software libre y los estándares abiertos, fomentar el desarrollo de aplicaciones institucionales con utilidad pública, lograr la autonomía,  soberanía e independencia tecnológicas dentro de la APF". En el artículo 63 se explicita que "cuando se trate de desarrollos basados en software libre, se respetarán las condiciones de su licenciamiento original [...]".

## Contribuir

Para contribuir al proyecto, se pide que se haga tomando en cuenta la guía de
contribución de [git](https://git-scm.com/book/es/v2/Git-en-entornos-distribuidos-Contribuyendo-a-un-Proyecto).