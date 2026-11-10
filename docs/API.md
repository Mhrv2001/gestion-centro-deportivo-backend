# Referencia de la API

Base local: `http://127.0.0.1:8000/api/`. Enviar cuerpos JSON con `Content-Type: application/json` y conservar la barra `/` final de las rutas. Esta configuración local no exige autenticación en los endpoints.

## Métodos y rutas

Cada uno de los recursos `profesores`, `actividades` e `inscripciones` tiene estas rutas:

| Método | Ruta de ejemplo | Función | Éxito |
|---|---|---|---|
| GET | `/api/profesores/` | Listar registros | 200 |
| POST | `/api/profesores/` | Crear registro | 201 |
| GET | `/api/profesores/1/` | Consultar un registro | 200 |
| PUT | `/api/profesores/1/` | Reemplazar campos editables de un registro | 200 |
| PATCH | `/api/profesores/1/` | Modificar solo los campos enviados | 200 |
| DELETE | `/api/profesores/1/` | Eliminar un registro | 204, sin cuerpo |

Sustituir `profesores` por `actividades` o `inscripciones` para sus respectivos CRUD. `GET /api/` muestra los tres recursos. Las listas son arreglos JSON sin paginación; una lista vacía responde `[]`.

## Modelos y relaciones

| Modelo | Campos principales | Relación / comportamiento |
|---|---|---|
| Profesor | nombre, especialidad, correo único | Un profesor tiene varias actividades |
| Actividad | nombre, categoría, horario, capacidad, precio, activa | `profesor` es una ForeignKey con PROTECT |
| Inscripcion | nombre y correo del participante, fecha | `actividad` es una ForeignKey con CASCADE |

No se puede eliminar un profesor mientras tenga actividades; la API responde 400 con un mensaje. Al eliminar una actividad también se eliminan sus inscripciones. Para conservar el historial sin eliminarlo, se puede marcar `activa=false`.

## 1. Crear profesor

`POST /api/profesores/`

```json
{
  "nombre": "Carlos Pérez",
  "especialidad": "Fútbol",
  "correo": "carlos@example.com"
}
```

Respuesta de ejemplo, HTTP 201:

```json
{
  "id": 1,
  "nombre": "Carlos Pérez",
  "especialidad": "Fútbol",
  "correo": "carlos@example.com"
}
```

Nombre, especialidad y correo son obligatorios. Los textos admiten hasta 100 caracteres; el correo debe ser válido, se guarda en minúsculas y la API rechaza otro profesor con el mismo correo sin distinguir mayúsculas. El ID lo genera la base. Usar el ID devuelto en la respuesta: los ejemplos no garantizan que sea 1.

`PATCH /api/profesores/1/` con `{"especialidad":"Entrenamiento"}` cambia solo esa especialidad.

## 2. Crear actividad

Primero debe existir el profesor indicado por su ID.

`POST /api/actividades/`

```json
{
  "nombre": "Fútbol",
  "categoria": "Equipo",
  "profesor": 1,
  "horario": "Lunes y miércoles 18:00",
  "capacidad": 15,
  "precio": "6000.00",
  "activa": true
}
```

La respuesta 201 incluye estos campos y agrega `id`, `profesor_nombre` y `cupos_disponibles`. El precio se devuelve como una cadena decimal, por ejemplo `"6000.00"`; en este proyecto representa pesos chilenos.

Reglas:

- Nombre, categoría, profesor, horario, capacidad y precio son obligatorios.
- Nombre, categoría y horario tienen un máximo de 100 caracteres.
- `capacidad` es un entero mayor o igual a 1.
- `precio` debe ser mayor o igual a 0; admite hasta 8 dígitos totales y 2 decimales.
- `activa` es booleano; si se omite en la creación, su valor predeterminado es `true`.
- `cupos_disponibles = capacidad - número de inscripciones`; es un campo de solo lectura.
- `profesor_nombre` también es de solo lectura. Para cambiar al profesor se envía su ID en `profesor`.
- No se puede reducir la capacidad por debajo del total de inscripciones existentes.

`PATCH /api/actividades/1/` con `{"precio":"6500.00"}` modifica el precio. `{"activa":false}` cierra nuevas inscripciones sin borrar las ya existentes.

## 3. Crear inscripción

`POST /api/inscripciones/`

```json
{
  "actividad": 1,
  "nombre_participante": "Ana López",
  "correo_participante": "ana@example.com"
}
```

Los tres campos son obligatorios. La respuesta 201 agrega `id`, `actividad_nombre` y `fecha_inscripcion` (fecha y hora ISO 8601 con zona horaria). Esos campos son de solo lectura.

Reglas:

- La actividad debe existir y estar activa para una inscripción nueva o un traslado.
- Debe quedar al menos un cupo. El cupo se calcula desde los registros reales, sin mantener un contador separado.
- Un mismo correo puede inscribirse en distintas actividades, pero no repetirse en la misma. Se ignoran las mayúsculas y se guarda el correo en minúsculas.
- `nombre_participante` admite hasta 100 caracteres y no puede estar vacío.
- Al cancelar con DELETE se elimina la inscripción y el cupo vuelve a estar disponible.

`PATCH /api/inscripciones/1/` con `{"nombre_participante":"Ana López González"}` conserva los campos que no se enviaron. También se puede cambiar el correo o trasladar la inscripción enviando otro ID de actividad. Al editar, el propio registro se excluye del cálculo de duplicados y cupos. Se permite corregir el contacto de una inscripción existente en una actividad desactivada; eso no agrega un nuevo participante.

Para PUT de una inscripción, enviar los tres campos editables del ejemplo de creación.

## Filtros y búsquedas

| Recurso | Parámetro | Ejemplo |
|---|---|---|
| Profesores | `search` en nombre o especialidad | `/api/profesores/?search=Yoga` |
| Actividades | `search` en nombre, categoría o nombre de profesor | `/api/actividades/?search=Carlos` |
| Actividades | `categoria`, coincidencia completa ignorando mayúsculas ASCII | `/api/actividades/?categoria=Equipo` |
| Actividades | `profesor`, ID entero positivo | `/api/actividades/?profesor=1` |
| Actividades | `activa`, true o false | `/api/actividades/?activa=true` |
| Inscripciones | `actividad`, ID entero positivo | `/api/inscripciones/?actividad=1` |
| Inscripciones | `correo`, coincidencia completa sin distinguir mayúsculas ASCII | `/api/inscripciones/?correo=ana@example.com` |

Los filtros se pueden combinar: `/api/actividades/?categoria=Equipo&profesor=1&activa=true`. La búsqueda no elimina tildes. Los parámetros declarados de ID o estado con valores inválidos devuelven 400; otros parámetros desconocidos se ignoran.

## Errores y respuestas

| Estado | Significado | Ejemplo |
|---|---|---|
| 200 | Consulta o actualización correcta | GET, PUT o PATCH válidos |
| 201 | Creación correcta | POST válido |
| 204 | Eliminación correcta | DELETE válido, cuerpo vacío |
| 400 | Datos o filtro inválidos | Precio negativo, correo repetido, falta de cupos |
| 404 | Recurso inexistente | ID que no existe |
| 405 | Método no permitido en esa ruta | PUT en una lista sin ID |

Error de ejemplo para una inscripción sin cupos, HTTP 400:

```json
{"actividad": ["No quedan cupos disponibles."]}
```

Error de correo repetido, HTTP 400:

```json
{"correo_participante": ["Este correo ya está inscrito."]}
```

Los mensajes de validación propios aparecen por campo. Django REST Framework puede traducir sus mensajes automáticos según el idioma configurado. Las respuestas inválidas no deben agregar registros ni aplicar parcialmente una actualización.

## Transacciones y persistencia

Las escrituras de los ViewSets se ejecutan dentro de `transaction.atomic`; SQLite utiliza `BEGIN IMMEDIATE` para serializar las escrituras antes de consultar cupos. Las restricciones de la base rechazan capacidad cero, precio negativo y el mismo correo ASCII con diferente capitalización en una actividad. Las validaciones de negocio adicionales se ejecutan en serializers y formularios administrativos.

Las transacciones no convierten SQLite en un servidor para alta concurrencia: si una escritura mantiene la base ocupada más que el timeout, puede ocurrir un bloqueo. La aplicación se entrega para evaluación local, sin autenticación obligatoria ni pruebas de carga.

## Verificación

Consultar [evidencias/README.md](../evidencias/README.md) para repetir las 25 pruebas de Django y las 35 solicitudes de la colección Postman. La evidencia JSON contiene las respuestas reales de esa ejecución, distintas de los ejemplos ilustrativos de este documento.
