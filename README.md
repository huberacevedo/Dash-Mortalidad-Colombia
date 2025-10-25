# Dash-Mortalidad-Colombia
Dash de Mortalidad en Colombia para la asignatura de Aplicaciones I
Introducción del proyecto

Esta aplicación web es un dashboard interactivo desarrollado como parte de la Actividad 4. La aplicación visualiza y analiza los datos de mortalidad en Colombia para el año 2019, proporcionando una herramienta accesible y completa para identificar patrones demográficos y regionales.

Objetivo

El objetivo principal de esta aplicación es transformar los microdatos de estadísticas vitales (defunciones no fetales) del DANE en representaciones visuales comprensibles. Esto permite identificar tendencias, patrones y correlaciones clave, como la distribución geográfica de las muertes, las variaciones temporales, las principales causas de defunción y las diferencias demográficas.

Estructura del proyecto

El repositorio está organizado de la siguiente manera:

app.py: El archivo principal de Python que contiene toda la lógica de la aplicación Dash, incluyendo la carga de datos, el procesamiento con Pandas y la generación de gráficos con Plotly.

requirements.txt: Un archivo de texto que lista todas las dependencias de Python necesarias para ejecutar la aplicación (usado por la plataforma de despliegue).

.gitignore: Archivo estándar para excluir archivos innecesarios del repositorio (como entornos virtuales o cachés).

README.md: Este archivo, que documenta el proyecto.

data/ (Recomendado): Se sugiere crear esta carpeta y almacenar allí los archivos CSV (Anexo1...csv, Anexo2...csv, Divipola...csv) para mantener el repositorio ordenado. Nota: Si pones los CSV en una carpeta data/, debes actualizar las rutas en app.py (ej: file_mortality = "data/Anexo1...").

Requisitos

Las principales librerías de Python y sus versiones (aproximadas) necesarias para ejecutar la aplicación son:

dash

dash-bootstrap-components

plotly

pandas

requests

gunicorn (para el despliegue)

Puedes instalar todas las dependencias ejecutando:
pip install -r requirements.txt

Despliegue en Render

Estos son los pasos seguidos para desplegar la aplicación en Render, una plataforma como servicio (PaaS):

Crear Repositorio en GitHub: Se subieron todos los archivos del proyecto (app.py, requirements.txt, .gitignore, README.md y los archivos CSV) a un nuevo repositorio en GitHub.

Crear Cuenta en Render: Se creó una cuenta gratuita en Render y se conectó con la cuenta de GitHub.

Nuevo Servicio Web: En el dashboard de Render, se seleccionó "New" -> "Web Service".

Conectar Repositorio: Se seleccionó el repositorio de GitHub creado en el paso 1.

Configurar el Servicio:

Name: Se asignó un nombre único a la aplicación (ej: dashboard-mortalidad-col).

Region: Se dejó la región por defecto (o se seleccionó la más cercana).

Branch: Se seleccionó la rama principal (main o master).

Runtime: Se seleccionó Python 3.

Build Command: pip install -r requirements.txt

Start Command: gunicorn app:server

Crear Servicio: Se hizo clic en "Create Web Service". Render automáticamente clonó el repositorio, instaló las dependencias y ejecutó el comando de inicio.

Acceder a la App: Una vez completado el despliegue, la aplicación estuvo disponible en la URL pública proporcionada por Render.

Software

Lenguaje: Python 3.x

Bibliotecas de Análisis: Pandas

Bibliotecas de Visualización y Web: Plotly, Dash, Dash Bootstrap Components

Servidor de Aplicaciones (Producción): Gunicorn

Plataforma de Despliegue (PaaS): Render

Instalación

Para clonar y ejecutar este proyecto localmente, sigue estos pasos:

Clonar el repositorio:

git clone [https://www.youtube.com/watch?v=n4tDI2jN0Ik](https://www.youtube.com/watch?v=n4tDI2jN0Ik)
cd [nombre-del-repositorio]


(Recomendado) Crear un entorno virtual:

python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate


Instalar las dependencias:

pip install -r requirements.txt


Asegurar los datos: Descarga los archivos CSV (Anexo1..., Anexo2..., Divipola...) y colócalos en la raíz del proyecto (o en una carpeta data/ y ajusta app.py).

Ejecutar la aplicación:

python app.py


Abre tu navegador y ve a http://127.0.0.1:8050/.
