from rest_framework.routers import DefaultRouter

from .views import ActividadViewSet, InscripcionViewSet, ProfesorViewSet


router = DefaultRouter()
router.register("profesores", ProfesorViewSet)
router.register("actividades", ActividadViewSet)
router.register("inscripciones", InscripcionViewSet)

urlpatterns = router.urls
