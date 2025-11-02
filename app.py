import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import requests # Para descargar el GeoJSON

# --- 1. Carga y Preparación de Datos ---

# URL del GeoJSON para el mapa de departamentos de Colombia
# --- CAMBIO 1: Usamos una URL de Gist más estable que no es bloqueada ---
geojson_url = "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e23951b3b1d34b7113b53a801121d1d8f8c/colombia.geo.json"

try:
    geojson_colombia = requests.get(geojson_url).json()
    print("GeoJSON de Colombia (Gist) cargado exitosamente.")
except Exception as e:
    print(f"Error al descargar o procesar el GeoJSON: {e}")
    geojson_colombia = None

# Nombres de los archivos CSV
# --- CAMBIO 2: Se usa la ruta 'Data/' (con 'D' mayúscula) para que coincida con tu repositorio de GitHub ---
file_mortality = "Data/Anexo1.NoFetal2019_CE_15-03-23.xlsx - No_Fetales_2019.csv"
file_codes = "Data/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx - Final.csv"
file_divipola = "Data/Divipola_CE_.xlsx - Hoja1.csv"

# Cargar los dataframes
try:
    # df_mort: Datos de mortalidad
    df_mort = pd.read_csv(file_mortality, dtype={'COD_DANE': str})
    
    # df_codes: Códigos de muerte
    df_codes = pd.read_csv(file_codes, skiprows=8)
    df_codes = df_codes.rename(columns={
        'Código de la CIE-10 cuatro caracteres': 'COD_MUERTE',
        'Descripcion  de códigos mortalidad a cuatro caracteres': 'CAUSA_MUERTE_NOMBRE'
    })
    
    # df_divipola: Nombres de municipios y departamentos
    df_divipola = pd.read_csv(file_divipola, dtype={'COD_DANE': str})
    
    print("Archivos CSV cargados exitosamente desde la carpeta 'Data/'.")

except FileNotFoundError as e:
    print(f"Error: No se encontró el archivo {e.filename}. Asegúrate de que los archivos CSV estén en el directorio 'Data/' (con D mayúscula).")
    df_mort = pd.DataFrame()
    df_codes = pd.DataFrame()
    df_divipola = pd.DataFrame()

# --- Procesamiento y Merges ---
if not df_mort.empty and not df_divipola.empty:
    df_full = pd.merge(
        df_mort,
        df_divipola[['COD_DANE', 'DEPARTAMENTO', 'MUNICIPIO']],
        on='COD_DANE',
        how='left'
    )
    df_full['DEPARTAMENTO'] = df_full['DEPARTAMENTO'].str.upper().str.strip()
else:
    df_full = pd.DataFrame() 

# --- 2. Creación de Gráficos (Funciones) ---

# Gráfico 1: Mapa - Muertes por Departamento
def create_map(df):
    if df.empty or geojson_colombia is None:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles para el mapa"))
        
    deaths_by_dept = df.groupby('DEPARTAMENTO').size().reset_index(name='Total Muertes')
    
    # Corrección de nombres para que coincidan con el GeoJSON (el Gist usa BOGOTÁ, D.C.)
    deaths_by_dept['DEPARTAMENTO'] = deaths_by_dept['DEPARTAMENTO'].replace({
        'ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA': 'ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA',
        'BOGOTÁ, D.C.': 'BOGOTÁ, D.C.'
    })
    
    # El 'featureidkey' 'DPTO_CNMBR' es correcto para el GeoJSON de Gist
    fig = px.choropleth_mapbox(
        deaths_by_dept,
        geojson=geojson_colombia,
        locations='DEPARTAMENTO',
        featureidkey="properties.DPTO_CNMBR", # Esto es correcto para el Gist
        color='Total Muertes',
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        zoom=4,
        center={"lat": 4.5709, "lon": -74.2973},
        opacity=0.7,
        title="Total de Muertes por Departamento (2019)"
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    return dcc.Graph(figure=fig)

# Gráfico 2: Líneas - Muertes por Mes
def create_line_chart(df):
    if df.empty:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles"))
        
    deaths_by_month = df.groupby('MES').size().reset_index(name='Total Muertes')
    deaths_by_month = deaths_by_month.sort_values(by='MES')
    meses = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 
             7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
    deaths_by_month['MES_NOMBRE'] = deaths_by_month['MES'].map(meses)
    
    fig = px.line(
        deaths_by_month,
        x='MES_NOMBRE',
        y='Total Muertes',
        title="Total de Muertes por Mes (2019)",
        markers=True
    )
    fig.update_layout(xaxis_title="Mes", yaxis_title="Total Muertes")
    return dcc.Graph(figure=fig)

# Gráfico 3: Barras - 5 Ciudades más Violentas (Homicidios X95)
def create_violent_cities_chart(df):
    if df.empty:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles"))
        
    homicides_df = df[df['COD_MUERTE'].str.startswith('X95', na=False)]
    
    violent_cities = homicides_df.groupby('MUNICIPIO').size().reset_index(name='Total Homicidios (X95)')
    top_5_violent = violent_cities.sort_values(by='Total Homicidios (X95)', ascending=False).head(5)
    
    fig = px.bar(
        top_5_violent,
        x='MUNICIPIO',
        y='Total Homicidios (X95)',
        title="Top 5 Ciudades más Violentas (Homicidios X95)",
        color='MUNICIPIO'
    )
    fig.update_layout(xaxis_title="Ciudad", yaxis_title="Total Homicidios")
    return dcc.Graph(figure=fig)

# Gráfico 4: Pie - 10 Ciudades con Menor Mortalidad
def create_low_mortality_chart(df):
    if df.empty:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles"))
        
    deaths_by_city = df.groupby('MUNICIPIO').size().reset_index(name='Total Muertes')
    deaths_by_city = deaths_by_city[deaths_by_city['Total Muertes'] > 0]
    
    bottom_10_cities = deaths_by_city.sort_values(by='Total Muertes', ascending=True).head(10)
    
    fig = px.pie(
        bottom_10_cities,
        names='MUNICIPIO',
        values='Total Muertes',
        title="10 Ciudades con Menor Índice de Mortalidad (Total)"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return dcc.Graph(figure=fig)

# Gráfico 5: Tabla - 10 Principales Causas de Muerte
def create_causes_table(df_mort, df_codes):
    if df_mort.empty or df_codes.empty:
        return html.Div("Datos no disponibles para la tabla de causas.")
        
    deaths_by_cause = df_mort.groupby('COD_MUERTE').size().reset_index(name='Total')
    
    merged_causes = pd.merge(
        deaths_by_cause,
        df_codes[['COD_MUERTE', 'CAUSA_MUERTE_NOMBRE']],
        on='COD_MUERTE',
        how='left'
    )
    
    merged_causes['CAUSA_MUERTE_NOMBRE'] = merged_causes['CAUSA_MUERTE_NOMBRE'].fillna('Desconocida o sin especificar')
    
    top_10_causes = merged_causes.sort_values(by='Total', ascending=False).head(10)
    
    top_10_causes = top_10_causes.rename(columns={
        'COD_MUERTE': 'Código CIE-10',
        'CAUSA_MUERTE_NOMBRE': 'Causa de Muerte',
        'Total': 'Total Casos'
    })
    
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

# Gráfico 6: Barras Apiladas - Muertes por Sexo en cada Departamento
def create_sex_by_dept_chart(df):
    if df.empty:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles"))
        
    deaths_by_dept_sex = df.groupby(['DEPARTAMENTO', 'SEXO']).size().reset_index(name='Total')
    
    sex_map = {1: 'Hombre', 2: 'Mujer', 9: 'Desconocido'}
    deaths_by_dept_sex['SEXO_ NOMBRE'] = deaths_by_dept_sex['SEXO'].map(sex_map).fillna('Desconocido')
    
    fig = px.bar(
        deaths_by_dept_sex,
        x='DEPARTAMENTO',
        y='Total',
        color='SEXO_ NOMBRE',
        title="Total de Muertes por Sexo y Departamento",
        barmode='stack'
    )
    fig.update_layout(xaxis_title="Departamento", yaxis_title="Total Muertes", xaxis_tickangle=-45)
    return dcc.Graph(figure=fig)

# Gráfico 7: Histograma - Distribución de Muertes por Grupo de Edad
def create_age_histogram(df):
    if df.empty:
        return dcc.Graph(figure=px.bar(title="Datos no disponibles"))
        
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
    
    category_order = [
        'Mortalidad neonatal', 'Mortalidad infantil', 'Primera infancia',
        'Niñez', 'Adolescencia', 'Juventud', 'Adultez temprana',
        'Adultez intermedia', 'Vejez', 'Longevidad', 'Edad desconocida'
    ]
    
    df['GRUPO_EDAD_CAT'] = df['GRUPO_EDAD1'].map(age_map)
    
    age_distribution = df['GRUPO_EDAD_CAT'].value_counts().reset_index()
    age_distribution.columns = ['Grupo de Edad', 'Total Muertes']
    
    age_distribution['Grupo de Edad'] = pd.Categorical(
        age_distribution['Grupo de Edad'],
        categories=category_order,
        ordered=True
    )
    age_distribution = age_distribution.sort_values('Grupo de Edad')
    
    fig = px.bar(
        age_distribution,
        x='Grupo de Edad',
        y='Total Muertes',
        title="Distribución de Muertes por Grupo de Edad"
    )
    fig.update_layout(xaxis_title="Grupo de Edad", yaxis_title="Total Muertes", xaxis_tickangle=-45)
    return dcc.Graph(figure=fig)


# --- 3. Inicialización de la App Dash ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server 

# --- 4. Layout de la Aplicación ---
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Dashboard de Mortalidad en Colombia - 2019",
                    className="text-center text-primary, mb-4 mt-4"
                ),
                width=12
            )
        ),
        
        dbc.Row(
            [
                dbc.Col(create_map(df_full), width=12, md=7, className="mb-4"),
                dbc.Col(create_line_chart(df_mort), width=12, md=5, className="mb-4"),
            ],
            align="center"
        ),
        
        dbc.Row(
            [
                dbc.Col(create_sex_by_dept_chart(df_full), width=12, lg=7, className="mb-4"),
                dbc.Col(create_age_histogram(df_mort), width=12, lg=5, className="mb-4"),
            ],
            align="center"
        ),
        
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
