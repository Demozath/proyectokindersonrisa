from django.views.generic import ListView
from .models import Llamada, TipoLlamada, Paciente
from .forms import LlamadaForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


class LlamadaListView(ListView):
    model = Llamada
    template_name = 'llamada_list.html'


def registrar_llamada(request):
    paciente_random = None
    show_form = False
    form = LlamadaForm()

    # Obtener todas las llamadas del usuario
    llamadas = Llamada.objects.filter(usuario=request.user)
    todos_los_tipos = TipoLlamada.objects.all()
    datos_por_tipo = {}
    for tipo in todos_los_tipos:
        conteo = llamadas.filter(tipo=tipo).count()
        datos_por_tipo[tipo.nombre] = {'conteo': conteo}

    if request.method == 'POST':
        if 'generar_llamada' in request.POST:
            paciente_random = Paciente.objects.filter(is_active=True).order_by('?').first()
            if paciente_random:
                show_form = True
            else:
                messages.warning(request, 'No se encontraron pacientes activos.')
        else:
            form = LlamadaForm(request.POST)
            paciente_rut = request.POST.get('paciente_rut')
            paciente = Paciente.objects.get(rut=paciente_rut)
            if form.is_valid() and paciente:
                llamada = form.save(commit=False)
                llamada.usuario = request.user
                llamada.paciente = paciente
                llamada.save()

                # Si la llamada es "No volver a llamar", se marca el paciente como inactivo
                if llamada.tipo.nombre == 'No volver a llamar':
                    paciente.is_active = False
                    paciente.save()

                messages.success(request, 'Llamada registrada con éxito.')
                return redirect('registrar_llamada')
            else:
                messages.error(request, 'Error al registrar la llamada. Asegúrese de haber seleccionado un paciente.')

    context = {
        'form': form,
        'paciente_random': paciente_random,
        'show_form': show_form,
        'datos_por_tipo': datos_por_tipo
    }
    return render(request, 'llamadas/registrar_llamada.html', context)
