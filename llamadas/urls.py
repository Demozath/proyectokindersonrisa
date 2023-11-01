from django.contrib import admin
from django.urls import path
from llamadas.views import LlamadaListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('llamadas/', LlamadaListView.as_view(), name='llamada-list'),

]
