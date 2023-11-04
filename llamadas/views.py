from django.views.generic import ListView
from .models import Llamada, TipoLlamada, Paciente, CustomUser
from .forms import LlamadaForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import datetime, timedelta
from django.db.models import Count
from django.utils.timezone import make_aware



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


def revisar_llamadas(request):
    template_name = 'llamadas/revisar_llamadas.html'

    tipos_llamadas = TipoLlamada.objects.all()
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if fecha_desde and fecha_hasta:
        fecha_desde = make_aware(datetime.strptime(fecha_desde, '%Y-%m-%d'))
        fecha_hasta = make_aware(datetime.strptime(fecha_hasta, '%Y-%m-%d'))
        fecha_hasta += timedelta(days=1) - timedelta(seconds=1)
        llamadas = Llamada.objects.filter(fecha__range=(fecha_desde, fecha_hasta))
    else:
        llamadas = Llamada.objects.all()

    usuarios_conteos = llamadas.values(
        'usuario__rut'
    ).annotate(total=Count('id')).order_by('-total')

    usuarios = []
    for usuario_conteo in usuarios_conteos:
        usuario_rut = usuario_conteo['usuario__rut']
        usuario = CustomUser.objects.get(rut=usuario_rut)
        usuario_conteo['nombre_completo'] = usuario.get_full_name()
        usuario_conteo['conteos'] = {
            tipo.nombre: llamadas.filter(
                usuario__rut=usuario_rut, tipo=tipo
            ).count() for tipo in tipos_llamadas
        }
        usuarios.append(usuario_conteo)

    total_general = sum(usuario['total'] for usuario in usuarios)
    context = {
        'usuarios': usuarios,
        'tipos_llamadas': tipos_llamadas,
        'total_general': total_general,  # Agregar esto al contexto
    }



    return render(request, template_name, context)