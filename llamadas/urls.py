from django.urls import path
from llamadas.views import LlamadaListView, registrar_llamada, revisar_llamadas, cargar_pacientes, gestionar_tipos_llamada


urlpatterns = [
    path('llamadas/', LlamadaListView.as_view(), name='llamada-list'),
    path('registrar_llamada/', registrar_llamada, name='registrar_llamada'),
    path('revisar_llamadas/', revisar_llamadas, name='revisar_llamadas'),
    path('cargar_pacientes/', cargar_pacientes, name='cargar_pacientes'),
    path('gestionar_tipos_llamada/', gestionar_tipos_llamada, name='gestionar_tipos_llamada'),





]
