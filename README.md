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

## Estructura del proyecto

```text
myallsupport-site102/
|- myapp.py
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

## Requisitos

- Python 3.9+ (recomendado)
- Flask instalado en el entorno

Instalacion basica:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install flask
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
