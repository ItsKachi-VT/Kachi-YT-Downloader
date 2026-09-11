# Kachi Downloader

![Estado: versión preliminar](https://img.shields.io/badge/estado-versi%C3%B3n%20preliminar-orange)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Código abierto](https://img.shields.io/badge/c%C3%B3digo-abierto-brightgreen)

Kachi Downloader es un descargador de videos y música de YouTube, pensado para
ser de fácil acceso, instalación sencilla y uso directo. Permite descargar
videos de hasta **1080p** y extraer audio en formato **MP3**, siempre que el
contenido y las herramientas disponibles lo permitan.

> **Importante:** este proyecto se encuentra en una versión muy preliminar.
> Algunas funciones, mensajes y casos de error todavía pueden cambiar. Por
> ahora, la forma recomendada de ejecutarlo es desde una consola mediante
> `app.py`.

## Características

- Descarga de videos en formato MP4 o MKV.
- Descarga y extracción de música en MP3.
- Resoluciones disponibles de 360p, 480p, 720p y 1080p.
- Historial local de descargas.
- Selección de la carpeta de destino.
- Detección y configuración de FFmpeg cuando es posible.
- Proyecto de código abierto y fácil de adaptar.

## Requisitos

- Windows.
- Python 3.10 o posterior.
- FFmpeg para combinar video y audio o extraer música.
- Conexión a Internet.

## Instalación

Clona o descarga el proyecto y abre una consola dentro de su carpeta:

```bash
python -m venv .venv
```

Activa el entorno virtual:

```powershell
.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación del entorno, puedes ejecutar directamente
el intérprete que se encuentra dentro de `.venv`.

## Ejecución recomendada

La aplicación debe iniciarse desde la consola ejecutando `app.py`:

```bash
python app.py
```

Después se abrirá la interfaz de la aplicación. Introduce una URL compatible,
elige el formato, la resolución y la carpeta de destino, y comienza la
descarga.

La aplicación puede descargar automáticamente `yt-dlp.exe` cuando lo necesita.
También intenta localizar FFmpeg o instalarlo mediante WinGet en Windows. Si no
se encuentra, instala FFmpeg manualmente y vuelve a ejecutar la aplicación.

## Crear un ejecutable

La creación del ejecutable está incluida como alternativa experimental. No es
el flujo principal de esta versión preliminar, pero permite generar una
versión distribuible con PyInstaller:

```bash
python build_installer.py
```

El resultado se genera en la carpeta `dist/` como `KachiDownloader.exe`.

También puedes preparar el entorno y compilarlo con estos comandos:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python build_installer.py
```

## Uso responsable

Usa Kachi Downloader únicamente con contenido que tengas autorización para
descargar. Respeta los derechos de autor, las condiciones de uso de YouTube y
la legislación aplicable en tu país. El proyecto no garantiza que todos los
enlaces o formatos funcionen siempre.

## Licencia

Este proyecto se distribuye bajo una licencia de uso personalizada. Se permite
usar, copiar, modificar, fusionar, publicar y distribuir el material para
cualquier fin.

Si el proyecto, sus modificaciones o derivados se utilizan con fines
comerciales, generan algún beneficio económico o incorporan mejoras
significativas, se agradece incluir una atribución o reconocimiento a
**@ItsKachi_VT**. Esta atribución es opcional y no constituye una condición de
uso, modificación o distribución.

También se agradece conservar el aviso de licencia en las copias sustanciales
del software o de la documentación cuando sea posible.

El software se proporciona **"tal cual"**, sin garantías de ningún tipo,
expresas o implícitas, incluyendo, entre otras, garantías de comerciabilidad,
idoneidad para un propósito particular y no infracción. Consulta el archivo
[`LICENSE`](LICENSE) para ver el texto completo de la licencia.

## Estado del proyecto

Este proyecto está en desarrollo activo y puede recibir cambios importantes en
la interfaz, la instalación y la generación del ejecutable. Los comentarios,
errores reproducibles y sugerencias son bienvenidos.
