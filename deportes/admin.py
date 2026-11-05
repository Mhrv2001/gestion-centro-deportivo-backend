from django.contrib import admin

from .models import Actividad, Inscripcion, Profesor


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre", "especialidad", "correo"]
    search_fields = ["nombre", "especialidad", "correo"]


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "nombre",
        "categoria",
        "profesor",
        "horario",
        "capacidad",
        "precio",
        "activa",
    ]
    list_filter = ["categoria", "activa"]
    search_fields = ["nombre", "categoria", "profesor__nombre"]


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "nombre_participante",
        "correo_participante",
        "actividad",
        "fecha_inscripcion",
    ]
    search_fields = [
        "nombre_participante",
        "correo_participante",
        "actividad__nombre",
    ]

# Register your models here.
