from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('controller.api.urls')),
    path('', views.index)
]
