from django.views.generic import ListView
from .models import Llamada

class LlamadaListView(ListView):
    model = Llamada
    template_name = 'llamada_list.html'
