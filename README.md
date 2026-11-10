# Gestión de Centro Deportivo — Backend

API REST del centro deportivo Locos X el Deporte, desarrollada con Python, Django, Django REST Framework y SQLite. Permite administrar profesores y actividades, registrar inscripciones y controlar los cupos disponibles mediante datos persistentes.

Este repositorio es independiente del frontend React de la primera evaluación. La API funciona localmente sin conectar React ni desplegar un servidor público.

## Requisitos

- Python 3.14, con `pip` y `venv`.
- Git si se descargará mediante clonación.
- Dependencias fijadas en `requirements.txt`: Django 6.1.3 y Django REST Framework 3.18.3, entre otras.
- Postman es opcional para explorar solicitudes. Node.js con npm solo se necesita para ejecutar la colección automáticamente con Newman.

## Instalación en Windows / PowerShell

```powershell
git clone https://github.com/Mhrv2001/gestion-centro-deportivo-backend.git
cd gestion-centro-deportivo-backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py cargar_ejemplos
.\.venv\Scripts\python.exe manage.py runserver
```

Se usa directamente el Python de `.venv`; no hace falta activar el entorno ni cambiar la política de ejecución de PowerShell. Si `python` no está disponible, comprobar la instalación de Python antes de continuar.

En Linux/macOS, crear el entorno con `python3 -m venv .venv` y sustituir `.\.venv\Scripts\python.exe` por `.venv/bin/python` en los comandos.

Abrir **http://127.0.0.1:8000/api/**. La raíz muestra enlaces a profesores, actividades e inscripciones y permite utilizar la interfaz navegable de Django REST Framework.

`runserver` mantiene la terminal ocupada: dejarla abierta mientras se usa la API. Para detenerlo, presionar `Ctrl + C`.

## Datos y panel administrativo

```powershell
.\.venv\Scripts\python.exe manage.py cargar_ejemplos
```

El comando crea tres profesores ficticios y actividades de fútbol, natación y yoga. Se puede repetir sin duplicar estos registros ni sobrescribir sus precios u horarios modificados. No incluye inscripciones ni contraseñas predeterminadas.

Para usar el administrador:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Ingresar una cuenta local propia y abrir **http://127.0.0.1:8000/admin/**. Esa cuenta no es necesaria para utilizar los endpoints de esta evaluación.

## Funcionalidades

- CRUD de profesores, actividades e inscripciones.
- Relaciones `Actividad → Profesor` e `Inscripcion → Actividad` mediante `ForeignKey`.
- Consulta de cupos calculada desde las inscripciones guardadas.
- Rechazo de nuevas inscripciones en actividades inactivas o llenas.
- Rechazo de un correo repetido en la misma actividad, ignorando mayúsculas.
- Cancelación de inscripciones con recuperación del cupo.
- Validación de capacidad mínima, precio no negativo y correos válidos.
- Imposibilidad de reducir la capacidad por debajo de los participantes inscritos.
- Filtros por categoría, profesor, estado activo, actividad y correo; búsqueda por texto.
- Formularios del administrador con validaciones de cupos y correos.

## Documentación y pruebas

- [Rutas, modelos, ejemplos JSON y errores](docs/API.md).
- [Evidencia HTTP e instrucciones de Postman/Newman](evidencias/README.md).
- [Colección importable en Postman](postman/centro_deportivo.postman_collection.json).
- [Declaración de uso de IA](USO_IA.md).
- [Guía para estudiar y practicar la defensa](docs/DEFENSA.md).

Revisar configuración, cambios de modelos pendientes y pruebas:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test deportes
```

Las 25 pruebas de Django usan una base de datos independiente y comprueban CRUD, relaciones, validaciones y formularios. No modifican los datos locales de trabajo.

Para repetir la evidencia de la colección, con Node.js y npm instalados:

```powershell
.\.venv\Scripts\python.exe herramientas/verificar_api.py
```

El script inicia su propio servidor en el puerto 8765 y utiliza una base temporal. El informe incluye 35 solicitudes, 45 comprobaciones y sus respuestas. Para utilizar la aplicación gráfica Postman, seguir [estas instrucciones](evidencias/README.md).

## Organización

```text
config/                  Configuración del proyecto y rutas principales
deportes/models.py       Tablas, relaciones y validaciones del administrador
deportes/serializers.py   Conversión a JSON y validación de solicitudes
deportes/views.py         CRUD, filtros y transacciones
deportes/urls.py          Registro de rutas con DefaultRouter
deportes/migrations/      Historial de cambios de la base de datos
deportes/tests.py         Pruebas automatizadas
deportes/management/      Comando cargar_ejemplos
postman/                 Colección de solicitudes
herramientas/            Generador de colección y ejecutor HTTP
evidencias/              Resultados reales e instrucciones de reproducción
docs/                    Referencia de API y guía de defensa
```

## Persistencia y configuración local

SQLite guarda los registros en `db.sqlite3`: detener y volver a iniciar el servidor conserva los datos. La base y `.venv` se excluyen de Git; las migraciones y `requirements.txt` permiten reconstruir el entorno en otro equipo. Después de clonar, cada integrante debe ejecutar `migrate` y, si desea datos ficticios, `cargar_ejemplos`.

La base puede cambiarse mediante la variable de entorno `DJANGO_DB_PATH`; la utiliza el ejecutor de pruebas HTTP para aislar sus datos. `DJANGO_SECRET_KEY` permite reemplazar la clave local de desarrollo. Estas variables se leen del entorno del proceso; no se carga automáticamente un archivo `.env`.

Las operaciones de escritura de la API usan `transaction.atomic` y SQLite con modo `IMMEDIATE` para validar y guardar dentro de una escritura serializada. Los cambios deben realizarse mediante la API o los formularios administrativos. Escrituras directas con el ORM omiten `clean()`; solo conservan las restricciones declaradas en la base de datos.

La configuración es para ejecución local de la evaluación: `DEBUG=True`, API sin autenticación obligatoria y servidor de desarrollo. No está preparada para exposición pública en producción ni se han realizado pruebas de carga.

## Trabajo en pareja

Cada integrante puede clonar este repositorio en su equipo. Antes de comenzar una modificación: `git pull`; después de terminar y probar una parte: `git add`, `git commit` y `git push`. Los commits registran avances reales y no sustituyen la comprensión individual del código.
