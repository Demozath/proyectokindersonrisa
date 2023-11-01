from django.urls import path
from llamadas.views import LlamadaListView


urlpatterns = [
    path('llamadas/', LlamadaListView.as_view(), name='llamada-list'),


]
