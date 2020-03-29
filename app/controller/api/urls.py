from django.urls import include, path

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('output', views.OutputViewSet, 'output')
router.register('position', views.PositionViewSet, 'position')
router.register('recordings', views.RecordingViewSet, 'recording-list')

urlpatterns = [
    path('', include(router.urls)),
]
