from rest_framework import viewsets

from .models import Actividad, Profesor
from .serializers import ActividadSerializer, ProfesorSerializer


class ProfesorViewSet(viewsets.ModelViewSet):
    queryset = Profesor.objects.all().order_by("id")
    serializer_class = ProfesorSerializer


class ActividadViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.select_related("profesor").all().order_by("id")
    serializer_class = ActividadSerializer
