# usuarios/urls.py

from django.urls import path
from .views import registro, login_view

urlpatterns = [
    path('registro/', registro, name='registro'),
    path('login/', login_view, name='login')
]
