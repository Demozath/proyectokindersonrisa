from django.views.generic import ListView
from .models import Llamada
from .forms import LlamadaForm
from django.shortcuts import render, redirect
from django.contrib import messages

class LlamadaListView(ListView):
    model = Llamada
    template_name = 'llamada_list.html'

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
    return render(request, 'llamadas/registrar_llamada.html', {'form': form})