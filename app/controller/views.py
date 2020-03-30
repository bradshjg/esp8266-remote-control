from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    context = {'api_hostport': settings.API_HOSTPORT}
    return render(request, 'controller/index.html', context=context)
