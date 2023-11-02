from django.views.generic import ListView
from .models import Llamada, TipoLlamada
from .forms import LlamadaForm
from django.shortcuts import render, redirect
from django.contrib import messages

class LlamadaListView(ListView):
    model = Llamada
    template_name = 'llamada_list.html'

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Llamada, TipoLlamada
from .forms import LlamadaForm

def registrar_llamada(request):
    if request.method == 'POST':
        form = LlamadaForm(request.POST)
        if form.is_valid():
            llamada = form.save(commit=False)
            llamada.usuario = request.user
            llamada.save()
            messages.success(request, 'Llamada registrada con éxito.')
            return redirect('registrar_llamada')
    else:
        form = LlamadaForm()

    # Obtenemos todas las llamadas del usuario actual
    llamadas = Llamada.objects.filter(usuario=request.user)

    # Traemos todos los tipos de llamada
    todos_los_tipos = TipoLlamada.objects.all()

    # Creamos un diccionario con el conteo de llamadas y comentarios por tipo para el usuario
    datos_por_tipo = {}
    for tipo in todos_los_tipos:
        conteo = llamadas.filter(tipo=tipo).count()
        comentarios = [llamada.comentario for llamada in llamadas.filter(tipo=tipo)]
        datos_por_tipo[tipo.nombre] = {
            'conteo': conteo,
            'comentarios': comentarios
        }

    return render(request, 'llamadas/registrar_llamada.html', {'form': form, 'datos_por_tipo': datos_por_tipo})


