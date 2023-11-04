from django.urls import path
from llamadas.views import LlamadaListView, registrar_llamada, revisar_llamadas


urlpatterns = [
    path('llamadas/', LlamadaListView.as_view(), name='llamada-list'),
    path('registrar_llamada/', registrar_llamada, name='registrar_llamada'),
    path('revisar_llamadas/', revisar_llamadas, name='revisar_llamadas'),




]
