from rest_framework import viewsets, permissions

from home.models import Canvas
from home.serializers import CanvasSerializer

class CanvasViewSet(viewsets.ModelViewSet):
    serializer_class = CanvasSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Canvas.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
