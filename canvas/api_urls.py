from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CanvasViewSet

router = DefaultRouter()
router.register(r'canvas', CanvasViewSet, basename='canvas')

urlpatterns = [
    path('', include(router.urls)),
]
