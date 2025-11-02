# ==============================================================================
# Dashboard de mortalidad en Colombia
# Maestria en IA - Aplicaciones I - Universidad de la Salle
# Presentado por: Huber Duvier Acevedo Hernandez y Laura Ximena Tirado Rairan
# Docente: Cristian Duney Bermudez Quintero
# Noviembre de 2025
# ==============================================================================

import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json # Importamos JSON para leer el archivo local

# Carga y Preparación de Datos

# Carga del GeoJSON desde un archivo local
# Se carga el mapa de Colombia desde un archivo 'colombia.geo.json' local.
# Esto evita problemas de red y bloqueos de URLs externas.
try:
    with open('colombia.geo.json', 'r', encoding='utf-8') as f:
        geojson_colombia = json.load(f)
    print("GeoJSON de Colombia (local) cargado exitosamente.")
except Exception as e:
    print(f"Error al cargar el GeoJSON local: {e}")
    geojson_colombia = None

# Nombres de los archivos Excel
# Apuntamos a los archivos .xlsx
file_mortality = "data/Anexo1.NoFetal2019_CE_15-03-23.xlsx"
file_codes = "data/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx"
file_divipola = "data/Divipola_CE_.xlsx"

# Cargar los dataframes
try:
    # Usamos pd.read_excel() y la librería openpyxl (definida en requirements.txt)
    
    # df_mort: Datos de mortalidad
    df_mort = pd.read_excel(file_mortality, sheet_name='No_Fetales_2019', dtype={'COD_DANE': str})
    
    # df_codes: Códigos de muerte
    # Saltamos las primeras 8 filas de encabezado del archivo Excel
    df_codes = pd.read_excel(file_codes, sheet_name='Final', skiprows=8)
    # Renombramos columnas para que sean más fáciles de usar
    df_codes = df_codes.rename(columns={
        'Código de la CIE-10 cuatro caracteres': 'COD_MUERTE',
        'Descripcion  de códigos mortalidad a cuatro caracteres': 'CAUSA_MUERTE_NOMBRE'
    })
    
    # df_divipola: Nombres de municipios y departamentos
    df_divipola = pd.read_excel(file_divipola, sheet_name='Hoja1', dtype={'COD_DANE': str})
    
    # Limpieza de las claves de 'COD_DANE' para eliminar espacios en blanco
    df_mort['COD_DANE'] = df_mort['COD_DANE'].astype(str).str.strip()
    df_divipola['COD_DANE'] = df_divipola['COD_DANE'].astype(str).str.strip()
    
    print("Archivos Excel (.xlsx) cargados exitosamente desde la carpeta data")

except FileNotFoundError as e:
    print(f"Error: No se encontró el archivo {e.filename}. Asegúrate de que los archivos Excel estén en el directorio data")
except Exception as e:
    # Este error es para alertar si los nombres de las hojas (sheet_name) son incorrectos
    print(f"Error al leer los archivos Excel: {e}. Asegúrate de que los nombres de las hojas sean correctos ('No_Fetales_2019', 'Final', 'Hoja1').")
    df_mort = pd.DataFrame()
    df_codes = pd.DataFrame()
    df_divipola = pd.DataFrame()


# Procesamiento y Merges
# Se unen los datos de mortalidad (df_mort) con los de división política (df_divipola)
# para obtener los nombres de DEPARTAMENTO y MUNICIPIO.
if not df_mort.empty and not df_divipola.empty:
    df_full = pd.merge(
        df_mort,
        df_divipola[['COD_DANE', 'DEPARTAMENTO', 'MUNICIPIO']],
        on='COD_DANE',
        how='left'
    )
 
    # Eliminamos filas donde el merge falló y 'DEPARTAMENTO' es Nulo
    df_full = df_full.dropna(subset=['DEPARTAMENTO'])
    
    # Se limpian y estandarizan los nombres de departamento
    df_full['DEPARTAMENTO'] = df_full['DEPARTAMENTO'].str.upper().str.strip()
else:
    df_full = pd.DataFrame() 

# Creación de Gráficos (Funciones)

# ==============================================================================
# Gráfico 1: Mapa
# Visualización de la distribución total de muertes por departamento.
# ==============================================================================
def create_map(df):
    if df.empty or geojson_colombia is None:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles para el mapa"))
        
    # 1. Agrupamos los datos para contar el total de muertes por departamento
    deaths_by_dept = df.groupby('DEPARTAMENTO').size().reset_index(name='Total Muertes')
    
    # 2. Normalizamos los nombres de los departamentos
    # Este mapa maneja todas las tildes y nombres especiales.
    name_map = {
        # Tildes
        'BOGOTA, D.C.': 'BOGOTÁ, D.C.',
        'BOLIVAR': 'BOLÍVAR',
        'BOYACA': 'BOYACÁ',
        'CAQUETA': 'CAQUETÁ',
        'CHOCO': 'CHOCÓ',
        'CORDOBA': 'CÓRDOBA',
        'GUAINIA': 'GUAINÍA',
        'NARINO': 'NARIÑO',
        'QUINDIO': 'QUINDÍO',
        'VAUPES': 'VAUPÉS',
        
        # Nombres especiales (Mapeo completo)
        'VALLE': 'VALLE DEL CAUCA',
        'GUAJIRA': 'LA GUAJIRA',
        'SAN ANDRES, PROVIDENCIA Y SANTA CATALINA': 'ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA'
    }
 # Aplicamos el reemplazo
    deaths_by_dept['DEPARTAMENTO'] = deaths_by_dept['DEPARTAMENTO'].replace(name_map)
    
    # 3. Creamos el mapa coroplético
    fig = px.choropleth_mapbox(
        deaths_by_dept,
        geojson=geojson_colombia,         # El mapa de fondo (local)
        locations='DEPARTAMENTO',         # Columna con los nombres a mapear
        featureidkey="properties.NOMBRE_DPT", # Clave para el GeoJSON
        color='Total Muertes',            # Columna que define el color
        color_continuous_scale="Viridis", # Escala de color
        mapbox_style="carto-positron",    # Estilo del mapa base
        zoom=4,                           # Nivel de zoom inicial
        center={"lat": 4.5709, "lon": -74.2973}, # Centro del mapa (Colombia)
        opacity=0.7,
        title="Total de Muertes por Departamento (2019)"
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    return dcc.Graph(figure=fig)

# ==============================================================================
# GRÁFICO 2: Gráfico de líneas
# Representación del total de muertes por mes.
# ==============================================================================
def create_line_chart(df):
    if df.empty:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles"))
        
    # 1. Agrupamos por 'MES' y contamos el total
    deaths_by_month = df.groupby('MES').size().reset_index(name='Total Muertes')
    deaths_by_month = deaths_by_month.sort_values(by='MES') # Ordenamos por mes
    
    # 2. Mapeamos los números de mes a nombres para mayor claridad
    meses = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 
             7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
    deaths_by_month['MES_NOMBRE'] = deaths_by_month['MES'].map(meses)
    
    # 3. Creamos el gráfico de líneas
    fig = px.line(
        deaths_by_month,
        x='MES_NOMBRE',
        y='Total Muertes',
        title="Total de Muertes por Mes (2019)",
        markers=True # Añadimos puntos en cada mes
    )
    fig.update_layout(xaxis_title="Mes", yaxis_title="Total Muertes")
    return dcc.Graph(figure=fig)

# ==============================================================================
# GRÁFICO 3: Gráfico de barras
# Visualización de las 5 ciudades más violentas (códigos X95).
# ==============================================================================
def create_violent_cities_chart(df):
    if df.empty:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles"))
        
    # 1. Filtramos los datos solo para homicidios con código X95
    homicides_df = df[df['COD_MUERTE'].str.startswith('X95', na=False)]
    
    # 2. Agrupamos por 'MUNICIPIO' y contamos los homicidios
    violent_cities = homicides_df.groupby('MUNICIPIO').size().reset_index(name='Total Homicidios (X95)')
    
    # 3. Ordenamos de mayor a menor y tomamos los 5 primeros (top 5)
    top_5_violent = violent_cities.sort_values(by='Total Homicidios (X95)', ascending=False).head(5)
    
    # 4. Creamos el gráfico de barras
    fig = px.bar(
        top_5_violent,
        x='MUNICIPIO',
        y='Total Homicidios (X95)',
        title="Top 5 Ciudades más Violentas (Homicidios X95)",
        color='MUNICIPIO'
    )
    fig.update_layout(xaxis_title="Ciudad", yaxis_title="Total Homicidios")
    return dcc.Graph(figure=fig)

# ==============================================================================
# GRÁFICO 4: Gráfico circular
# Muestra las 10 ciudades con menor índice de mortalidad.
# ==============================================================================
def create_low_mortality_chart(df):
    if df.empty:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles"))
        
    # 1. Agrupamos por 'MUNICIPIO' y contamos el total de muertes
    deaths_by_city = df.groupby('MUNICIPIO').size().reset_index(name='Total Muertes')
    
    # 2. Filtramos municipios con 0 muertes (si existen) para no distorsionar el gráfico
    deaths_by_city = deaths_by_city[deaths_by_city['Total Muertes'] > 0] 
    
    # 3. Ordenamos de menor a mayor (ascending=True) y tomamos las 10 primeras
    bottom_10_cities = deaths_by_city.sort_values(by='Total Muertes', ascending=True).head(10)
    
    # 4. Creamos el gráfico circular (pie chart)
    fig = px.pie(
        bottom_10_cities,
        names='MUNICIPIO',
        values='Total Muertes',
        title="10 Ciudades con Menor Índice de Mortalidad (Total)"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return dcc.Graph(figure=fig)

# ==============================================================================
# GRÁFICO 5: Tabla
# Listado de las 10 principales causas de muerte (código, nombre, total).
# ==============================================================================
def create_causes_table(df_mort, df_codes):
    if df_mort.empty or df_codes.empty:
        return html.Div("Datos no disponibles para la tabla de causas.")
        
    # 1. Contamos el total de muertes por 'COD_MUERTE'
    deaths_by_cause = df_mort.groupby('COD_MUERTE').size().reset_index(name='Total')
    
    # 2. Unimos (merge) con df_codes para obtener el nombre de la causa
    merged_causes = pd.merge(
        deaths_by_cause,
        df_codes[['COD_MUERTE', 'CAUSA_MUERTE_NOMBRE']],
        on='COD_MUERTE',
        how='left'
    )
    
    # 3. Limpiamos valores nulos si un código no tiene nombre
    merged_causes['CAUSA_MUERTE_NOMBRE'] = merged_causes['CAUSA_MUERTE_NOMBRE'].fillna('Desconocida o sin especificar')
    
    # 4. Ordenamos de mayor a menor y tomamos las 10 principales
    top_10_causes = merged_causes.sort_values(by='Total', ascending=False).head(10)
    
    # 5. Renombramos las columnas para la tabla final
    top_10_causes = top_10_causes.rename(columns={
        'COD_MUERTE': 'Código CIE-10',
        'CAUSA_MUERTE_NOMBRE': 'Causa de Muerte',
        'Total': 'Total Casos'
    })
    
    # 6. Creamos el componente Dash DataTable
    return dash_table.DataTable(
        data=top_10_causes.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in top_10_causes.columns],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'fontFamily': 'sans-serif',
            'padding': '10px'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
    )

# ==============================================================================
# GRÁFICO 6: Gráfico de barras apiladas
# Comparación del total de muertes por sexo en cada departamento.
# ==============================================================================
def create_sex_by_dept_chart(df):
    if df.empty:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles"))
        
    # 1. Agrupamos por 'DEPARTAMENTO' y 'SEXO'
    deaths_by_dept_sex = df.groupby(['DEPARTAMENTO', 'SEXO']).size().reset_index(name='Total')
    
    # 2. Mapeamos los códigos de 'SEXO' a nombres
    sex_map = {1: 'Hombre', 2: 'Mujer', 9: 'Desconocido'}
    deaths_by_dept_sex['SEXO_NOMBRE'] = deaths_by_dept_sex['SEXO'].map(sex_map).fillna('Desconocido')
    
    # 3. Creamos el gráfico de barras, usando 'color' para apilar
    fig = px.bar(
        deaths_by_dept_sex,
        x='DEPARTAMENTO',
        y='Total',
        color='SEXO_NOMBRE',       # Esto crea las secciones apiladas
        title="Total de Muertes por Sexo y Departamento",
        barmode='stack'            # Modo 'apilado'
    )
    fig.update_layout(xaxis_title="Departamento", yaxis_title="Total Muertes", xaxis_tickangle=-45)
    return dcc.Graph(figure=fig)

# ==============================================================================
# GRÁFICO 7: Histograma
# Distribución de muertes por GRUPO_EDAD1.
# ==============================================================================
def create_age_histogram(df):
    if df.empty:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles"))
        
    # 1. Creamos el diccionario que mapea códigos (0-29) a las categorías de edad
    age_map = {
        0: 'Mortalidad neonatal', 1: 'Mortalidad neonatal', 2: 'Mortalidad neonatal', 3: 'Mortalidad neonatal', 4: 'Mortalidad neonatal',
        5: 'Mortalidad infantil', 6: 'Mortalidad infantil',
        7: 'Primera infancia', 8: 'Primera infancia',
        9: 'Niñez', 10: 'Niñez',
        11: 'Adolescencia',
        12: 'Juventud', 13: 'Juventud',
        14: 'Adultez temprana', 15: 'Adultez temprana', 16: 'Adultez temprana',
        17: 'Adultez intermedia', 18: 'Adultez intermedia', 19: 'Adultez intermedia',
        20: 'Vejez', 21: 'Vejez', 22: 'Vejez', 23: 'Vejez', 24: 'Vejez',
        25: 'Longevidad', 26: 'Longevidad', 27: 'Longevidad', 28: 'Longevidad',
        29: 'Edad desconocida'
    }
    
    # 2. Creamos una lista con el orden deseado para el eje X
    category_order = [
        'Mortalidad neonatal', 'Mortalidad infantil', 'Primera infancia',
        'Niñez', 'Adolescencia', 'Juventud', 'Adultez temprana',
        'Adultez intermedia', 'Vejez', 'Longevidad', 'Edad desconocida'
    ]
    
    # 3. Aplicamos el mapeo para crear la nueva columna categórica
    df['GRUPO_EDAD_CAT'] = df['GRUPO_EDAD1'].map(age_map)
    
    # 4. Contamos los valores para cada categoría
    age_distribution = df['GRUPO_EDAD_CAT'].value_counts().reset_index()
    age_distribution.columns = ['Grupo de Edad', 'Total Muertes']
    
    # 5. Aplicamos el orden categórico para que el gráfico se muestre correctamente
    age_distribution['Grupo de Edad'] = pd.Categorical(
        age_distribution['Grupo de Edad'],
        categories=category_order,
        ordered=True
    )
    age_distribution = age_distribution.sort_values('Grupo de Edad')
    
    # 6. Creamos el gráfico de barras (que funciona como histograma para categorías)
    fig = px.bar(
        age_distribution,
        x='Grupo de Edad',
        y='Total Muertes',
        title="Distribución de Muertes por Grupo de Edad"
    )
    fig.update_layout(xaxis_title="Grupo de Edad", yaxis_title="Total Muertes", xaxis_tickangle=-45)
    return dcc.Graph(figure=fig)


# Inicialización de la App Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server # Necesario para el despliegue en Gunicorn

# Layout de la Aplicación
# Se define la estructura de la página web usando Dash Bootstrap Components (dbc)
app.layout = dbc.Container(
    fluid=True,
    children=[
        # Fila de Título
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Dashboard de Mortalidad en Colombia - 2019",
                    className="text-center text-primary, mb-4 mt-4" # Clases de Bootstrap
                ),
                width=12
            )
        ),
        
        # Fila 1: Mapa (Gráfico 1) y Gráfico de Líneas (Gráfico 2)
        dbc.Row(
            [
                dbc.Col(create_map(df_full), width=12, md=7, className="mb-4"),
                dbc.Col(create_line_chart(df_mort), width=12, md=5, className="mb-4"),
            ],
            align="center"
        ),
        
        # Fila 2: Barras Apiladas (Gráfico 6) e Histograma (Gráfico 7)
        dbc.Row(
            [
                dbc.Col(create_sex_by_dept_chart(df_full), width=12, lg=7, className="mb-4"),
                dbc.Col(create_age_histogram(df_mort), width=12, lg=5, className="mb-4"),
            ],
            align="center"
        ),
        
        # Fila 3: Tabla de Causas (Gráfico 5)
        dbc.Row(
            dbc.Col(
                [
                    html.H3("Top 10 Causas de Muerte", className="text-center mb-3"),
                    create_causes_table(df_mort, df_codes)
                ],
                width=12,
                className="mb-4"
            )
        ),
        
        # Fila 4: Ciudades Violentas (Gráfico 3) y Menor Mortalidad (Gráfico 4)
        dbc.Row(
            [
                dbc.Col(create_violent_cities_chart(df_full), width=12, md=6, className="mb-4"),
                dbc.Col(create_low_mortality_chart(df_full), width=12, md=6, className="mb-4"),
            ],
            align="center"
        ),
    ]
)

# --- 5. Ejecución de la App ---
if __name__ == '__main__':
    app.run_server(debug=True)


