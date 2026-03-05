# MyAllSupport Site 102

Aplicacion web sencilla en Flask para consultar variables de salud del entorno de ejecucion:

- Estado de Docker (si corre dentro de contenedor y hostname del contenedor)
- Estado de InterSystems IRIS (variable `IRISSYS`, binario `iris`, y proceso activo)
- Fecha, hora y uptime del proceso Flask

La aplicacion ofrece interfaz HTML y endpoint JSON para monitoreo.

## Objetivo del proyecto

Este proyecto busca entregar un panel ligero de diagnostico para ambientes IRIS/WSGI, util para validaciones rapidas operativas sin agregar complejidad de frontend ni build tools.

## Stack tecnologico

- Python 3
- Flask 3.x
- Templates Jinja2 (HTML renderizado en servidor)
- CSS embebido en templates para una UI simple y portable

## Arquitectura del proyecto (estado actual)

Este repositorio se ejecuta en una arquitectura de 3 capas dentro del mismo contenedor:

1. Editor y desarrollo:
- VS Code conectado directamente al contenedor Docker mediante `Dev Containers: Attach to Running Container`.
- Contenedor usado actualmente: `IRIS105`.

2. Runtime Python/Flask:
- El codigo vive clonado dentro del filesystem del contenedor.
- Flask entrega la app WSGI definida en `myapp.py`.

3. Publicacion web en IRIS:
- En InterSystems IRIS existe una Web Application configurada con tipo `WSGI`.
- Dicha Web Application apunta a la carpeta dentro del contenedor donde esta clonado este repo.
- El acceso final se publica bajo el prefijo web, por ejemplo: `/csp/myapp/`.

Resumen de flujo de solicitud HTTP:

`Navegador -> Web Gateway/IRIS Web Application (WSGI) -> myapp.py (Flask) -> respuesta HTML/JSON`

## Estructura del proyecto

```text
myallsupport-site102/
|- myapp.py
|- requirements.txt
|- templates/
|  |- index.html
|  |- server.html
|- .gitignore
|- README.md
```

## Funcionalidad

### 1) Pantalla raiz (`/`)

Muestra una portada con alternativas para navegar a:

- Pantalla de variables del server (`/server`)
- API JSON de salud (`/health`)

### 2) Pantalla de variables (`/server`)

Muestra en formato visual:

- Bloque Docker
- Bloque IRIS Server
- Bloque Proceso Flask

### 3) API de salud (`/health`)

Retorna un JSON con estructura:

```json
{
  "status": "ok",
  "docker": {
    "running_in_container": true,
    "container_hostname": "..."
  },
  "iris": {
    "irissys": "...",
    "iris_executable": "...",
    "iris_process_running": false
  },
  "process": {
    "pid": 123,
    "uptime_seconds": 10.23,
    "date_local": "2026-03-05",
    "time_local": "12:34:56",
    "datetime_utc": "2026-03-05T18:34:56+00:00"
  }
}
```

Notas:

- `running_in_container` se detecta usando `/.dockerenv` y `/proc/1/cgroup`.
- `iris_process_running` se estima buscando procesos con `ps -eo args=`.
- `iris_executable` usa `shutil.which("iris")`.

## Rutas disponibles

- `GET /` -> UI de inicio
- `GET /server` -> UI de variables del servidor
- `GET /health` -> API JSON de estado

## Soporte para despliegue bajo prefijo (`/csp/myapp/`)

La app usa `url_for(...)` para construir enlaces internos, lo que permite funcionar correctamente cuando esta publicada bajo un prefijo, por ejemplo:

- `http://localhost:52773/csp/myapp/`
- `http://localhost:52773/csp/myapp/server`
- `http://localhost:52773/csp/myapp/health`

## Replicar en otro Docker con IRIS

Esta guia permite levantar el mismo proyecto en otro contenedor que tenga InterSystems IRIS.

### 1) Crear o iniciar contenedor IRIS

Levanta un contenedor IRIS (imagen y puertos segun tu entorno). Debes tener disponible al menos el puerto web de IRIS.

Ejemplo de verificacion:

```bash
docker ps
```

### 2) Adjuntarte al contenedor desde VS Code

1. En VS Code, abre la paleta de comandos.
2. Ejecuta `Dev Containers: Attach to Running Container...`.
3. Selecciona el contenedor IRIS destino.
4. Abre una carpeta de trabajo dentro del contenedor (por ejemplo `/usr/irissys/csp/`).

### 3) Clonar el repositorio dentro del contenedor

Dentro del terminal de VS Code ya conectado al contenedor:

```bash
cd /usr/irissys/csp
git clone https://github.com/christianasmussenb/myallsupport-site102.git
cd myallsupport-site102
```

### 4) Verificar dependencias Python

La app usa dependencias definidas en `requirements.txt`.

```bash
python3 -c "import flask; print('flask ok')"
```

Si falta Flask, instala los requerimientos en la ruta de Python que usa IRIS/WSGI dentro del contenedor:

```bash
pip install --target /usr/irissys/mgr/python -r requirements.txt --upgrade
```

Importante:

- No instales `datetime` con pip. `datetime` es parte de la libreria estandar de Python.

### 5) Configurar Web Application en IRIS (tipo WSGI)

En el Management Portal de IRIS:

1. Ve a `System Administration` -> `Security` -> `Applications` -> `Web Applications`.
2. Crea (o edita) una aplicacion web, por ejemplo ruta: `/csp/myapp`.
3. En el tipo de aplicacion selecciona `WSGI`.
4. Configura el path fisico para que apunte al repo clonado dentro del contenedor, por ejemplo:
   `/usr/irissys/csp/myallsupport-site102`
5. Define el modulo/entrypoint WSGI segun tu plantilla de IRIS para Flask (archivo `myapp.py`, objeto app `app`).
6. Guarda los cambios.

Nota:

- Los nombres exactos de campos pueden variar entre versiones de IRIS/Web Gateway, pero la idea es siempre: ruta web (`/csp/myapp`) + tipo `WSGI` + carpeta del proyecto + entrypoint Flask.

### 6) Probar la publicacion

Desde navegador o curl:

```bash
curl -i http://localhost:52773/csp/myapp/
curl -i http://localhost:52773/csp/myapp/server
curl -i http://localhost:52773/csp/myapp/health
```

Debes obtener:

- HTML en `/` y `/server`
- JSON en `/health`

### 7) Checklist de troubleshooting

- Si `/csp/myapp/` devuelve error 404:
  confirma que la Web Application exista exactamente con esa ruta.
- Si hay error WSGI al cargar:
  revisa ruta fisica, permisos y entrypoint (`myapp.py` / variable `app`).
- Si enlaces internos salen sin prefijo:
  verificar que la publicacion pase correctamente el `SCRIPT_NAME` desde IRIS/Web Gateway.
- Si `iris_executable` aparece `not-found`:
  valida `PATH` dentro del proceso que ejecuta WSGI.

## Requisitos

- Python 3.9+ (recomendado)
- Dependencias de `requirements.txt`

Instalacion basica:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Instalacion para Docker + IRIS WSGI (desde shell del contenedor):

```bash
cd /usr/irissys/csp/myallsupport-site102
pip install --target /usr/irissys/mgr/python -r requirements.txt --upgrade
```

## Ejecucion local

Desde la carpeta del proyecto:

```bash
python3 myapp.py
```

Por defecto levanta en:

- `http://localhost:5000/`

Puerto configurable con variable de entorno:

```bash
PORT=8080 python3 myapp.py
```

## Pruebas rapidas

### Validar endpoint JSON

```bash
curl -s http://localhost:5000/health | python3 -m json.tool
```

### Validar sintaxis

```bash
python3 -m py_compile myapp.py
```

## Consideraciones operativas

- Este servicio es informativo; no ejecuta acciones administrativas.
- Los chequeos de IRIS son de nivel basico (deteccion de binario/proceso).
- Si necesitas un healthcheck estricto de IRIS (por ejemplo, query real al motor), se puede extender con una verificacion activa adicional.

## Posibles mejoras

- Endpoint `/health/live` con auto-refresh desde la UI.
- Separar estilos en archivos estaticos (`static/`).
- Agregar autenticacion basica para proteger la pantalla de variables.
- Incorporar tests unitarios para funciones de chequeo.

## Licencia

Sin licencia declarada en este repositorio.
