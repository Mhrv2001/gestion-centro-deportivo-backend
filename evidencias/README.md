# Pruebas de la API

`postman_resultado.json` contiene resultados reales de una ejecución de la colección mediante Newman 6.2.1, el ejecutor de colecciones de Postman. No es una captura de la aplicación gráfica Postman.

Resultado registrado: **35 solicitudes HTTP, 45 comprobaciones y 0 fallos**. Incluye respuestas JSON, estados esperados y errores de validación. Solo se utilizaron datos ficticios creados en una base SQLite temporal.

## Repetir la ejecución automática

Requiere las dependencias de Python instaladas y Node.js con npm disponible. Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe herramientas/verificar_api.py
```

El script crea una base temporal, aplica migraciones, abre un servidor propio en el puerto **8765**, ejecuta Newman y actualiza el informe. Al terminar cierra ese servidor y elimina la base temporal. El `db.sqlite3` de trabajo se conserva. El puerto 8765 debe estar libre y la primera ejecución necesita Internet para descargar Newman desde npm.

## Usar la aplicación Postman

1. Iniciar Django normalmente: `.\.venv\Scripts\python.exe manage.py runserver`.
2. En Postman elegir **Import** y seleccionar `postman/centro_deportivo.postman_collection.json`.
3. Confirmar que la variable de colección `base_url` sea `http://127.0.0.1:8000`.
4. Ejecutar **toda la colección en orden** desde Collection Runner.
5. Revisar los tests de cada solicitud y exportar el resultado o guardar una captura para la presentación.

La colección crea sus propios IDs y usa correos ficticios diferentes en cada ejecución. Al completarse elimina sus propios registros de prueba; si se interrumpe, esos registros pueden permanecer en la base utilizada por Postman. Las solicitudes de error esperan HTTP 400 o 404: recibir esos códigos en esas pruebas es el resultado correcto.

## Pruebas de Django

```powershell
.\.venv\Scripts\python.exe manage.py test deportes
```

Hay **25 pruebas automatizadas**: CRUD, persistencia, filtros, cupos, duplicados, transferencias, restricciones de SQLite y validaciones de formularios del administrador. Django crea una base de prueba separada y la descarta al finalizar. Estas pruebas no representan una prueba de carga de producción.

Si se modifica la colección, su fuente está en `herramientas/generar_coleccion.cjs`. Se regenera con `node herramientas/generar_coleccion.cjs`.
