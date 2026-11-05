from rest_framework.routers import DefaultRouter

from .views import ProfesorViewSet


router = DefaultRouter()
router.register("profesores", ProfesorViewSet)

urlpatterns = router.urls