from rest_framework import status, viewsets
from rest_framework.response import Response

from .serializers import OutputSerializer, PositionSerializer, RecordingSerializer


class RecordingViewSet(viewsets.ModelViewSet):
    serializer_class = RecordingSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.serializer_class.Meta.model.objects.all()
        return self.request.user.recordings.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        pass


class ActionBaseViewSet(viewsets.ViewSet):
    NOT_IMPLEMENTED_MESSAGE = {'info': 'Cannot currently read from device.'}
    serializer_class = None
    http_method_names = ['get', 'post']

    def retrieve(self, request, *args, **kwargs):
        return Response(self.NOT_IMPLEMENTED_MESSAGE)

    def list(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OutputViewSet(ActionBaseViewSet):
    serializer_class = OutputSerializer


class PositionViewSet(ActionBaseViewSet):
    serializer_class = PositionSerializer
