from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('controller.api.urls')),
    path('accounts/login/', LoginView.as_view()),
    path('', views.index)
]
