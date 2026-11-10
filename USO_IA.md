# Declaración de uso de inteligencia artificial

## Herramienta y alcance

Se utilizó ChatGPT/Codex durante el desarrollo del backend como asistente para proponer código, explicar conceptos, localizar errores, ejecutar verificaciones y redactar documentación. Parte del trabajo se realizó siguiendo instrucciones manualmente y otra parte mediante edición directa del asistente en el computador.

## Estimación por archivo

Las siguientes cifras describen aproximadamente la proporción de código o texto propuesto con asistencia de IA. Son estimaciones basadas en el desarrollo de este proyecto, no resultados de un detector ni mediciones automáticas. Copiar y ejecutar una propuesta no convierte esa propuesta en código redactado de forma independiente. Los integrantes deben revisar y confirmar esta declaración antes de entregar.

| Archivo o grupo | Estimación de contenido propuesto por IA | Descripción |
|---|---:|---|
| `deportes/models.py` | 90–100% | Propuesta de modelos, relaciones, validaciones y restricciones |
| `deportes/serializers.py` | 90–100% | Conversión a JSON, validación y correcciones para actualizaciones parciales |
| `deportes/views.py` | 90–100% | ViewSets, filtros, transacciones y tratamiento de eliminación protegida |
| `deportes/urls.py` y `config/urls.py` | 90–100% | Registro y conexión de rutas de la API |
| `deportes/admin.py` | 90–100% | Registro de modelos y configuración del administrador |
| `config/settings.py` | 10–20% | Cambios sobre la plantilla generada por Django: apps, SQLite, idioma, zona horaria y configuración local |
| `deportes/tests.py` | 90–100% | Propuesta e implementación de pruebas automáticas |
| `deportes/management/commands/cargar_ejemplos.py` | 90–100% | Comando de carga de ejemplos reproducibles |
| `herramientas/` y colección `postman/` | 90–100% | Generación de solicitudes, comprobaciones y ejecución automatizada |
| README y documentos de `docs/` | 90–100% | Redacción inicial de instrucciones, referencia y material de estudio |

Las migraciones fueron generadas por Django y `requirements.txt` por pip mediante comandos guiados. Los informes de `evidencias/` contienen resultados producidos al ejecutar las herramientas, no resultados inventados por el asistente.

## Preguntas de reflexión

### 1. ¿En qué aspectos se utilizó inteligencia artificial?

En la planificación de la estructura del backend, el código de la API, validaciones de negocio, resolución de errores, pruebas, ejemplos de uso y documentación. También se solicitaron explicaciones paso a paso para comprender los archivos.

### 2. ¿Qué partes se realizaron principalmente por los estudiantes?

Matías realizó manualmente la creación de la carpeta y el entorno virtual, instalación de dependencias, ejecución de comandos de Django y migraciones, edición inicial siguiendo las propuestas, creación del repositorio en GitHub y varios commits y subidas. Posteriormente autorizó que el asistente completara partes del código, verificaciones y documentación. No se atribuyen aquí contribuciones de otro integrante que no hayan sido confirmadas.

### 3. ¿Qué errores o problemas se encontraron?

Durante la integración aparecieron imports de clases inexistentes por archivos sin guardar, un `urls.py` sin `urlpatterns` y un import circular al importar serializers desde el mismo archivo. La propuesta inicial de validación de inscripciones tampoco manejaba correctamente los datos omitidos en PATCH ni excluía la propia inscripción al contar cupos y duplicados. Esos casos se corrigieron y se cubrieron con pruebas. También se alinearon las validaciones del administrador con las de la API.

### 4. ¿Cómo se verificó que el código sugerido funcionaba?

Se ejecutó `manage.py check`, se revisó la coherencia entre modelos y migraciones y se probaron solicitudes mediante Django REST Framework. La suite contiene 25 pruebas automatizadas. La colección Postman se ejecutó con Newman contra un servidor real y una base temporal: 35 solicitudes y 45 comprobaciones sin fallos. Las evidencias e instrucciones están en `evidencias/`.

### 5. ¿Qué conocimientos se adquirieron durante el desarrollo?

Los contenidos trabajados son entornos virtuales, modelos y relaciones, migraciones, serializers, métodos HTTP, CRUD, validaciones, filtros, pruebas y Git. La reflexión personal de cada integrante sobre qué comprendió y qué necesita practicar **está pendiente de completar durante el ensayo de defensa**. Esta declaración no afirma dominio individual sin comprobarlo.

## Revisión antes de entregar

Cada integrante debe revisar las estimaciones, completar su reflexión personal y poder explicar y modificar el código. La guía `docs/DEFENSA.md` permite practicar esa comprensión. El historial de commits registra cambios realizados, con asistencia cuando correspondió; no acredita por sí solo dominio técnico individual.
