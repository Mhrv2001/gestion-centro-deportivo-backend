# Uso de inteligencia artificial

Para este backend se utilizó ChatGPT/Codex como apoyo para escribir código, resolver errores y entender cómo funciona Django. La herramienta propuso buena parte del código de la API y también hizo modificaciones directamente en el proyecto.

Esta declaración describe el uso de la herramienta en el proyecto presentado en pareja. Las tareas y aprendizajes individuales deben ser revisados por cada integrante.

## En qué se utilizó

| Archivos | Apoyo recibido | Nivel aproximado |
|---|---|---|
| `models.py` | Propuesta de modelos, relaciones y validaciones | Alto |
| `serializers.py` | Código inicial y correcciones de cupos, duplicados y actualizaciones | Alto |
| `views.py` | CRUD, filtros y transacciones | Alto |
| `urls.py` y `admin.py` | Rutas y configuración del administrador | Alto |
| `settings.py` | Ajustes sobre la configuración que genera Django | Menor, limitado a ajustes |
| `tests.py` | Redacción y ejecución de pruebas | Alto |
| Carga de ejemplos y herramientas de Postman | Código y solicitudes de prueba | Alto |
| README y documentación | Redacción y revisión | Alto |

Los niveles son estimaciones del apoyo recibido, no porcentajes medidos. Las migraciones las generó Django y la lista de dependencias se obtuvo con pip, siguiendo instrucciones del asistente.

## Preguntas de la pauta

**¿En qué aspectos del proyecto se utilizó IA?**

En los modelos, serializers, vistas, rutas, validaciones, pruebas y documentación. También se pidieron explicaciones de las líneas de código y ayuda para resolver errores.

**¿Qué partes se realizaron manualmente?**

Las tareas manuales registradas incluyen crear la carpeta y el entorno virtual, instalar dependencias, copiar y ajustar el código siguiendo las indicaciones, ejecutar migraciones, crear el repositorio y realizar las primeras subidas. Más adelante se pidió al asistente completar código y pruebas. Las propuestas de código se consideran asistidas aunque se hayan copiado manualmente.

**¿Qué errores o problemas aparecieron?**

Hubo archivos sin guardar, imports en el archivo equivocado y rutas sin `urlpatterns`. También hubo un import circular en `serializers.py`. La validación inicial de inscripciones necesitó correcciones para permitir PATCH y para no contar la misma inscripción como duplicada o como un cupo adicional.

**¿Cómo se comprobó que funcionaba?**

Con `manage.py check`, las migraciones, 25 pruebas de Django y una colección Postman ejecutada con Newman. Esa colección completó 35 solicitudes y 45 comprobaciones sin fallos. Los resultados están guardados en `evidencias`.

**¿Qué conocimientos se adquirieron?**

Durante el desarrollo se trabajaron modelos, relaciones, migraciones, serializers, CRUD, filtros, validaciones y Git. Falta que cada integrante complete su reflexión personal después de practicar la defensa: qué puede explicar por su cuenta, qué cambio puede realizar y qué necesita seguir estudiando.
