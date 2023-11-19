from django.urls import path
from llamadas.views import registrar_llamada, revisar_llamadas, cargar_pacientes, gestionar_tipos_llamada, pacientes_no_llamar, gestion_usuarios


urlpatterns = [
    path('registrar_llamada/', registrar_llamada, name='registrar_llamada'),
    path('revisar_llamadas/', revisar_llamadas, name='revisar_llamadas'),
    path('cargar_pacientes/', cargar_pacientes, name='cargar_pacientes'),
    path('gestionar_tipos_llamada/', gestionar_tipos_llamada, name='gestionar_tipos_llamada'),
    path('pacientes_no_llamar/', pacientes_no_llamar, name='pacientes_no_llamar'),
    path('gestion_usuarios/', gestion_usuarios, name='gestion_usuarios'),


]
