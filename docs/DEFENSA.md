# Guía de estudio y defensa

Este documento es material para practicar. Leerlo no acredita que cada integrante ya domine el proyecto. Trabajar una idea por vez, abrir el archivo correspondiente y comprobar un ejemplo antes de avanzar.

## Primer bloque: ubicar archivos

| Si preguntan por... | Abrir... | Idea para explicar con palabras propias |
|---|---|---|
| Tablas y relaciones | `deportes/models.py` | Cada clase representa una tabla; ForeignKey relaciona registros |
| Datos recibidos y JSON | `deportes/serializers.py` | Valida lo que llega y transforma los modelos para responder |
| Solicitudes y filtros | `deportes/views.py` | Los ViewSets ofrecen las operaciones CRUD y seleccionan registros |
| Direcciones web | `deportes/urls.py` y `config/urls.py` | El router crea las rutas y el proyecto las incluye bajo `/api/` |
| Base de datos e idioma | `config/settings.py` | Configura las apps instaladas, SQLite y el entorno local |
| Cambios de tablas | `deportes/migrations/` | Guarda instrucciones para actualizar el esquema |
| Verificación | `deportes/tests.py` | Prueba comportamientos correctos y casos que deben rechazarse |

## Segundo bloque: una solicitud de principio a fin

Al consultar `GET /api/actividades/`, las rutas llevan a `ActividadViewSet`, el queryset consulta SQLite y `ActividadSerializer` prepara la respuesta JSON. GET no crea una actividad.

Al enviar `POST /api/inscripciones/`, el router llama al ViewSet, el serializer revisa campos, actividad, cupos y correo, y solo si todo es válido se guarda el modelo en SQLite. Se devuelve HTTP 201 y la inscripción creada. Si falla una validación, responde 400 y no agrega el registro.

La vista base `EscrituraAtomicaViewSet` usa transacciones en create, update y destroy. `PATCH` termina utilizando el método update de Django REST Framework con validación parcial. En SQLite, el modo IMMEDIATE permite comenzar la escritura antes de consultar cupos, serializando estas operaciones locales.

## Tercer bloque: reglas de inscripciones

1. Una actividad tiene una capacidad máxima.
2. Los cupos se calculan restando sus inscripciones; no se modifica un contador manual.
3. Un correo no puede aparecer dos veces en la misma actividad.
4. Crear o trasladar una inscripción requiere una actividad activa con cupos.
5. Una actualización de contacto puede conservar una inscripción existente en una actividad desactivada.
6. Al actualizar se excluye la propia inscripción del conteo de cupos y duplicados.
7. DELETE elimina la inscripción, por lo que el cupo vuelve a estar disponible.

Ejercicio oral: explicar qué pasaría si hay capacidad 2 y una inscripción. Después, explicar qué sucede al crear la segunda, intentar una tercera y cancelar una.

## Presentación de cuatro minutos

| Tiempo aproximado | Qué mostrar |
|---|---|
| 0:00–0:35 | Problema: administrar actividades, profesores e inscripciones del centro deportivo |
| 0:35–1:15 | Tres modelos, dos ForeignKey y archivo SQLite persistente |
| 1:15–2:30 | Crear profesor, crear actividad, registrar inscripción y consultar cupos |
| 2:30–3:20 | Intento de duplicado o actividad llena, respuesta 400; cancelación y recuperación del cupo |
| 3:20–4:00 | Filtros, evidencia de pruebas, repositorio y documentación |

Elegir de antemano solicitudes de la colección Postman. No ejecutar toda la colección durante la explicación de cuatro minutos; mostrar una selección y tener el informe completo disponible. Usar nombres y correos ficticios.

## Preguntas técnicas para practicar

**¿Qué hace un modelo?** Define campos y relaciones que Django utiliza para trabajar con tablas. `models.py` no es la base de datos: sus datos se guardan en SQLite.

**¿Qué hace ForeignKey?** Una actividad guarda el ID del profesor al que pertenece. La relación inversa permite consultar las actividades de ese profesor. Una inscripción funciona igual con su actividad.

**¿Por qué PROTECT y CASCADE?** PROTECT impide borrar un profesor que aún tiene actividades. CASCADE elimina las inscripciones cuando se borra su actividad. Desactivar una actividad conserva los registros.

**¿GET y POST?** GET consulta; POST crea. PUT envía los campos editables para reemplazar un registro, PATCH cambia solo algunos y DELETE elimina.

**¿Qué hace un serializer?** Convierte instancias del modelo a datos que se pueden devolver como JSON y valida datos recibidos antes de guardar. El renderizado JSON final lo hace REST Framework.

**¿Qué hace ModelViewSet?** Incluye el comportamiento CRUD estándar. `queryset` selecciona registros y `serializer_class` elige su serializer.

**¿Qué hacen makemigrations y migrate?** El primero genera archivos a partir de cambios de los modelos. El segundo aplica esas instrucciones a la base de datos. No hace falta crear una migración por editar una vista o una validación del serializer.

**¿Dónde se impide el precio negativo?** En el validador del campo `precio` del modelo y en una restricción CHECK de SQLite. REST Framework recoge los validadores del modelo para la API.

**¿Por qué SQLite?** La pauta lo permite y facilita la instalación local. Guarda datos reales. Admite varias lecturas, pero serializa las escrituras; no se afirma un límite fijo de usuarios ni que esta configuración sea para producción.

**¿Qué pasa al reiniciar Django?** Los registros permanecen en el archivo SQLite. Ejecutar migrate tampoco elimina por sí mismo todos los datos existentes.

**¿Por qué no subir db.sqlite3 ni .venv?** Cada equipo reconstruye tablas y entorno con migraciones y dependencias. No deben compartirse datos personales o instalaciones locales como parte del código.

**¿Qué significan los estados HTTP?** 200 consulta/actualización, 201 creación, 204 eliminación sin contenido, 400 datos inválidos, 404 recurso inexistente. Un 400 esperado puede ser una prueba correcta.

**¿Qué se ha probado?** 25 pruebas automatizadas de Django y una colección Postman ejecutada con Newman: 35 solicitudes y 45 comprobaciones. El informe es de esa ejecución; no demuestra pruebas de carga ni comprensión individual.

## Cambios pequeños para practicar en vivo

Hacerlos durante el ensayo en una rama de práctica (`git switch -c practica-defensa`) o una copia. No subir ejercicios sin revisar. Guardar, ejecutar `manage.py check` y probar la solicitud después de cada cambio.

### A. Buscar también por correo de profesor

En `ProfesorViewSet` de `deportes/views.py`, cambiar:

```python
search_fields = ["nombre", "especialidad", "correo"]
```

Probar `GET /api/profesores/?search=example.com`. Explicar por qué editar esta lista no requiere migraciones.

### B. Agregar filtro por especialidad

Dentro de `ProfesorViewSet` agregar:

```python
def get_queryset(self):
    profesores = super().get_queryset()
    especialidad = self.request.query_params.get("especialidad")
    if especialidad:
        profesores = profesores.filter(especialidad__iexact=especialidad)
    return profesores
```

Probar `GET /api/profesores/?especialidad=Yoga` y otra especialidad sin registros.

### C. Exigir precio mínimo de 1000 en la API

Dentro de `ActividadSerializer`, agregar esta validación del campo:

```python
def validate_precio(self, precio):
    if precio < 1000:
        raise serializers.ValidationError("El precio mínimo es 1000.")
    return precio
```

Probar PATCH con precio 500 (400) y 1000 (200). Explicar que esta regla nueva solo está en el serializer; si se desea aplicarla también al administrador y la base, deben modificarse el validador y la restricción del modelo y generar su migración.

## Forma de estudiar

Practicar en bloques breves: abrir un archivo, señalar tres líneas y decir qué hace cada una. Después ejecutar un ejemplo. Si una pregunta resulta difícil, consultar el archivo y volver a explicarlo con palabras propias. No memorizar una respuesta que no se pueda relacionar con el código.

Antes de la entrega, cada integrante debe completar su reflexión personal en `USO_IA.md`, verificar su acceso al repositorio y ensayar una modificación sin copiar una solución completa.
