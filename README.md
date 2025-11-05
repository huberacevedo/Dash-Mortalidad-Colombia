# Dashboard Interactivo de Mortalidad en Colombia (2019)

Este repositorio contiene la Actividad 4: Aplicación web interactiva para el análisis de mortalidad en Colombia para la asignatura "Aplicaciones I" de la Maestría en Inteligencia Artificial. Es un dashboard web interactivo construido para analizar las estadísticas de mortalidad en Colombia durante el año 2019, utilizando datos oficiales del DANE.

## Presentado por:
Huber Duvier Acevedo Hernandez y 
Laura Ximena Tirado Rairan

## URL de la aplicación desplegada:
https://dash-mortalidad-colombia-5y92.onrender.com/

## GitHub: 
https://github.com/huberacevedo/Dash-Mortalidad-Colombia/tree/main


# Introducción del Proyecto
Este proyecto puso en práctica nuestras habilidades en el procesamiento de datos y desarrollo web. El resultado es una aplicación web dinámica, construida con Dash y Plotly, que permite a cualquier usuario explorar visualmente los datos complejos de mortalidad en Colombia. Dejamos atrás las herramientas estáticas para ofrecer una herramienta interactiva y accesible desde cualquier navegador.

# Objetivo
El objetivo principal de esta aplicación es analizar los datos de mortalidad de Colombia del año 2019 para identificar patrones, tendencias y correlaciones clave. Buscamos responder preguntas como:
¿Cómo se distribuyeron geográficamente las muertes en el país?
¿Hubo picos de mortalidad en algunos meses?
¿Cuáles fueron las principales causas de muerte?
¿Cómo varía la mortalidad por sexo o grupo de edad?
¿Qué ciudades presentaron los índices más altos de violencia (homicidios)?

# Estructura del Proyecto
El repositorio está organizado de la forma más simple posible para facilitar el despliegue en plataformas PaaS como Render:
/
│
├── app.py                      # El corazón de la app: código Dash, lógica de Pandas y gráficas de Plotly.
├── requirements.txt            # Lista de librerías de Python necesarias para el despliegue.
├── colombia.geo.json           # Archivo GeoJSON local con los polígonos de los departamentos.
│
├── data/Anexo1.NoFetal2019_CE_15-03-23.xlsx    # Datos brutos de mortalidad (DANE).
├── data/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx # Datos brutos de los códigos CIE-10 (DANE).
├── data/Divipola_CE_.xlsx           # Datos brutos de la División Política (DANE).
│
├── .gitignore                  # Archivo para ignorar archivos de entorno virtual y caché.
├── LICENSE                     # Licencia del proyecto (MIT).
└── README.md                   # Esta documentación.


# Requisitos
El proyecto se construyó con Python 3.10. Las librerías principales y sus versiones (incluidas en requirements.txt) son:
dash
dash-bootstrap-components
plotly
pandas
openpyxl (necesario para que Pandas pueda leer archivos .xlsx)
gunicorn (para el despliegue en el servidor web de Render)


# Despliegue en Render
Estos fueron los pasos que seguimos para desplegar la aplicación en Render de forma gratuita:
Repositorio en GitHub: Se creó un repositorio y se subieron todos los archivos del proyecto a la raíz (root) del mismo.
Crear Web Service: En el dashboard de Render, seleccionamos "New" > "Web Service" y lo conectamos a nuestro repositorio de GitHub.
Configuración del Build:
Environment: Python 3
Build Command: pip install -r requirements.txt (Esto instala todas las librerías).
Configuración de Inicio:
Start Command: gunicorn app:server (Esto le dice a Gunicorn que busque el objeto server dentro del archivo app.py).
Despliegue: Se lanzó el primer despliegue manual. A partir de ese momento, Render se configuró para redesplegar automáticamente con cada push a la rama main.

# Software y Herramientas
Lenguaje: Python 3.10
Análisis de Datos: Pandas
Framework Web y Visualización: Dash, Plotly y Dash Bootstrap Components.
Servidor de Aplicación: Gunicorn
Plataforma de Despliegue (PaaS): Render
Control de Versiones: Git y GitHub

# Instalación y Ejecución Local
Si quieres clonar este proyecto y ejecutarlo en tu máquina local, solo sigue estos pasos:
Clonar el repositorio:
git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)
cd TU_REPOSITORIO


# Crear y activar un entorno virtual (recomendado):
# En macOS/Linux
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
.\venv\Scripts\activate


Instalar las dependencias:
pip install -r requirements.txt


Ejecutar la aplicación:
python app.py


Abre tu navegador y ve a http://127.0.0.1:8050/.

# Visualizaciones y Hallazgos
A continuación, se presenta un resumen de los 7 elementos visuales del dashboard y los hallazgos que permiten.

# 1. Mapa: Total de Muertes por Departamento
Descripción: Un mapa coroplético que muestra la distribución geográfica de la mortalidad total. Los departamentos con colores más intensos (escala 'Viridis') indican un mayor número de defunciones.
Hallazgos: Permite identificar rápidamente las zonas del país con mayor carga de mortalidad, que (como es de esperarse) se correlaciona con los departamentos de mayor densidad poblacional.


# 2. Gráfico de Líneas: Total de Muertes por Mes
Descripción: Muestra la fluctuación de las muertes a lo largo de los 12 meses del año 2019.
Hallazgos: Se pueden observar picos estacionales. (Aquí puedes añadir si viste algún pico en enero o a mitad de año, comúnmente asociados a temporadas de enfermedades respiratorias).


# 3. Gráfico de Barras: Top 5 Ciudades más Violentas
Descripción: Un gráfico de barras enfocado en un subconjunto de datos: homicidios (códigos CIE-10 que inician con X95). Muestra las 5 ciudades con más casos.
Hallazgos: Este gráfico es un indicador directo de las zonas urbanas que enfrentaron mayores desafíos de seguridad y violencia durante ese año.


# 4. Gráfico Circular: 10 Ciudades con Menor Mortalidad
Descripción: Un gráfico de pastel que destaca los 10 municipios con el menor número absoluto de muertes registradas (excluyendo aquellos con cero muertes).
Hallazgos: Generalmente, estos son municipios con muy baja densidad poblacional, lo que explica sus bajos números absolutos de mortalidad.


# 5. Tabla: Top 10 Causas de Muerte
Descripción: Una tabla interactiva que lista las 10 principales causas de muerte, mostrando su código CIE-10, el nombre de la enfermedad o causa, y el total de casos.
Hallazgos: Permite ver qué enfermedades (como las isquémicas del corazón o cerebrovasculares) dominan el perfil epidemiológico del país, en contraste con causas externas.


# 6. Barras Apiladas: Muertes por Sexo y Departamento
Descripción: Compara el total de muertes por departamento, pero apilando las barras para diferenciar entre "Hombre" y "Mujer".
Hallazgos: Hace evidente las diferencias de género en la mortalidad. En muchos departamentos, es visible una sobremortalidad masculina.


# 7. Histograma: Distribución por Grupo de Edad
Descripción: Agrupa la edad de los fallecidos en las categorías definidas (desde mortalidad neonatal hasta longevidad) y muestra la distribución en un gráfico de barras.
Hallazgos: Muestra claramente que la gran mayoría de las muertes se concentran en los grupos de "Vejez" y "Adultez intermedia", reflejando la esperanza de vida.

