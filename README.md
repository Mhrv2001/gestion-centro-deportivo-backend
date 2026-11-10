# Centro deportivo - Backend

Backend de Locos X el Deporte para la segunda evaluación. Es la continuación del proyecto de React, pero funciona por separado. Permite administrar profesores y actividades, inscribir participantes y controlar los cupos.

Se utilizó Python 3.14, Django, Django REST Framework y SQLite. Las versiones de las dependencias están en `requirements.txt`.

## Qué permite hacer

- Crear, consultar, modificar y eliminar profesores, actividades e inscripciones.
- Buscar y filtrar actividades.
- Ver cuántos cupos quedan y recuperar un cupo al cancelar una inscripción.
- Evitar inscripciones repetidas o en actividades llenas e inactivas.
- Validar correos, precios y capacidad.

Los modelos son `Profesor`, `Actividad` e `Inscripcion`. Cada actividad tiene un profesor y cada inscripción pertenece a una actividad.

## Cómo ejecutarlo

En Windows, abrir PowerShell y ejecutar:

```powershell
git clone https://github.com/Mhrv2001/gestion-centro-deportivo-backend.git
cd gestion-centro-deportivo-backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py cargar_ejemplos
.\.venv\Scripts\python.exe manage.py runserver
```

Después abrir http://127.0.0.1:8000/api/ en el navegador. Hay que dejar la terminal abierta mientras se usa el servidor. Para detenerlo, presionar `Ctrl + C`.

`cargar_ejemplos` agrega tres profesores y actividades de fútbol, natación y yoga. Se puede ejecutar otra vez sin duplicar esos datos ni cambiar los que ya existen. Los ejemplos usan correos ficticios.

Los registros quedan guardados en `db.sqlite3`, incluso después de cerrar el servidor. Ese archivo y la carpeta `.venv` no se suben a GitHub. Al descargar el proyecto en otro equipo hay que instalar las dependencias y ejecutar las migraciones.

## Rutas principales

| Ruta | Información |
|---|---|
| `/api/profesores/` | Profesores |
| `/api/actividades/` | Actividades y cupos |
| `/api/inscripciones/` | Inscripciones |

En esas rutas se puede consultar con GET y crear con POST. Para consultar, modificar o eliminar un registro específico se agrega su ID, por ejemplo `/api/actividades/1/`. PUT reemplaza sus datos, PATCH modifica algunos campos y DELETE lo elimina.

Los ejemplos completos y los filtros están en [docs/API.md](docs/API.md).

## Pruebas

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test deportes
```

Se aprobaron 25 pruebas de Django. También hay una [colección para importar en Postman](postman/centro_deportivo.postman_collection.json), ejecutada con Newman: 35 solicitudes y 45 comprobaciones sin fallos. Las instrucciones y resultados están en [evidencias](evidencias/README.md).

## Administrador

Para ingresar al panel, primero crear una cuenta local:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Después abrir http://127.0.0.1:8000/admin/. Las rutas de la API no requieren esa cuenta para esta evaluación.

## Archivos importantes

- `models.py`: modelos, relaciones y validaciones.
- `serializers.py`: validación de solicitudes y conversión de datos.
- `views.py`: operaciones CRUD y filtros.
- `urls.py`: direcciones de la API.
- `tests.py`: pruebas automáticas.

Estos archivos están dentro de `deportes`. La configuración general está en `config`.

El proyecto está preparado para uso local. No se conectó a React ni se desplegó en producción. La declaración de herramientas utilizadas está en [USO_IA.md](USO_IA.md) y el material para practicar la presentación está en [docs/DEFENSA.md](docs/DEFENSA.md).
