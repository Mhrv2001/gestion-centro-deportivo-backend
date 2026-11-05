from rest_framework.routers import DefaultRouter

from .views import ActividadViewSet, ProfesorViewSet


router = DefaultRouter()
router.register("profesores", ProfesorViewSet)
router.register("actividades", ActividadViewSet)

urlpatterns = router.urls
