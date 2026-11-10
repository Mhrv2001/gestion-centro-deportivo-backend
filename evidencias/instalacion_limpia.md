# Verificación desde una instalación limpia

Fecha de la comprobación: **10 de noviembre de 2026**.

Se clonó el repositorio remoto en una carpeta temporal distinta del proyecto de trabajo. Se creó un entorno virtual nuevo, se instalaron las dependencias exclusivamente desde `requirements.txt` y se generó una base SQLite nueva. No se copió el `db.sqlite3` ni la `.venv` del proyecto original.

Revisión de código comprobada: `980cf48` (las incorporaciones posteriores de esta entrega son documentación). Entorno: Windows, Python **3.14.4**, Django **6.1.3** y Django REST Framework **3.18.3**.

| Comprobación ejecutada | Resultado observado |
|---|---|
| Clonación desde GitHub | Correcta |
| `python -m venv .venv` | Entorno nuevo creado |
| `python -m pip install -r requirements.txt` usando el Python nuevo | Dependencias instaladas correctamente |
| `manage.py migrate --noinput` | Migraciones de Django y ambas migraciones de deportes aplicadas |
| `manage.py check` | Sin errores |
| `manage.py makemigrations --check --dry-run` | No changes detected |
| `manage.py test deportes` | 25 pruebas aprobadas, 0 fallos |
| `manage.py cargar_ejemplos`, primera ejecución | 3 profesores y 3 actividades creados |
| `manage.py cargar_ejemplos`, segunda ejecución | Los mismos registros, sin duplicados |
| Consulta desde un proceso Python posterior | 3 profesores, 3 actividades y 0 inscripciones persistentes |
| GET a `/api/`, `/api/profesores/`, `/api/actividades/` y `/api/inscripciones/` con el cliente DRF | HTTP 200 en las cuatro rutas |

Los resultados de las solicitudes HTTP contra un servidor real están documentados por separado en `postman_resultado.json`: 35 solicitudes y 45 comprobaciones, sin fallos, ejecutadas con Newman en otra base temporal. La consulta desde el cliente DRF de esta comprobación limpia no se presenta como una captura de Postman.

Para repetir la instalación, seguir el README desde la clonación y ejecutar los comandos de pruebas. El entorno verificado se creó en el mismo computador; no se afirma que se haya probado en otro sistema operativo o en producción.
