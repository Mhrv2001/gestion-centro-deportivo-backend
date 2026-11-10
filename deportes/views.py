from django.db import transaction
from django.db.models.deletion import ProtectedError
from rest_framework import filters, serializers, viewsets

from .models import Actividad, Inscripcion, Profesor
from .serializers import (
    ActividadSerializer,
    InscripcionSerializer,
    ProfesorSerializer,
)


class EscrituraAtomicaViewSet(viewsets.ModelViewSet):
    # Validar y guardar forman una sola transacción para no sobrepasar los cupos.
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


def filtro_id(parametros, nombre):
    valor = parametros.get(nombre)
    if valor is None:
        return None
    try:
        numero = int(valor)
    except (ValueError, TypeError):
        numero = 0
    if numero < 1:
        raise serializers.ValidationError({nombre: "Debe ser un identificador positivo."})
    return numero


class ProfesorViewSet(EscrituraAtomicaViewSet):
    queryset = Profesor.objects.all().order_by("id")
    serializer_class = ProfesorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "especialidad"]

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise serializers.ValidationError(
                {"profesor": "Primero elimina o reasigna las actividades de este profesor."}
            )


class ActividadViewSet(EscrituraAtomicaViewSet):
    queryset = Actividad.objects.select_related("profesor").all().order_by("id")
    serializer_class = ActividadSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "categoria", "profesor__nombre"]

    def get_queryset(self):
        actividades = super().get_queryset()
        parametros = self.request.query_params
        if parametros.get("categoria"):
            actividades = actividades.filter(categoria__iexact=parametros["categoria"])
        profesor = filtro_id(parametros, "profesor")
        if profesor is not None:
            actividades = actividades.filter(profesor_id=profesor)
        if "activa" in parametros:
            activa = parametros["activa"].lower()
            if activa not in ("true", "false"):
                raise serializers.ValidationError({"activa": "Usa true o false."})
            actividades = actividades.filter(activa=activa == "true")
        return actividades


class InscripcionViewSet(EscrituraAtomicaViewSet):
    queryset = Inscripcion.objects.select_related("actividad").all().order_by("id")
    serializer_class = InscripcionSerializer

    def get_queryset(self):
        inscripciones = super().get_queryset()
        parametros = self.request.query_params
        actividad = filtro_id(parametros, "actividad")
        if actividad is not None:
            inscripciones = inscripciones.filter(actividad_id=actividad)
        if parametros.get("correo"):
            inscripciones = inscripciones.filter(
                correo_participante__iexact=parametros["correo"].strip()
            )
        return inscripciones
