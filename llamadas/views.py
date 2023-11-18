from django.views.generic import ListView
from .models import Llamada, TipoLlamada, Paciente, CustomUser
from .forms import LlamadaForm, TipoLlamadaForm, CambiarEstadoTipoLlamadaForm, PacienteForm
from django.contrib import messages
from django.utils.timezone import datetime, timedelta
from django.db.models import Count
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required, user_passes_test
import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

class LlamadaListView(ListView):
    model = Llamada
    template_name = 'llamada_list.html'


def registrar_llamada(request):
    paciente_random = None
    show_form = False
    form = LlamadaForm()
    ultima_llamada = None

    llamadas = Llamada.objects.filter(usuario=request.user)

    tipos_llamada_activos = TipoLlamada.objects.filter(activo=True)

    datos_por_tipo = {}
    for tipo in tipos_llamada_activos:
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

                if llamada.tipo.nombre == 'No volver a llamar':
                    paciente.is_active = False
                    paciente.save()

                messages.success(request, 'Llamada registrada con éxito.')
                return redirect('registrar_llamada')
            else:
                messages.error(request, 'Error al registrar la llamada. Asegúrese de haber seleccionado un paciente.')
    if request.method == 'POST':
        if 'generar_llamada' in request.POST:
            paciente_random = Paciente.objects.filter(is_active=True).order_by('?').first()
            if paciente_random:
                show_form = True
                ultima_llamada = Llamada.objects.filter(paciente=paciente_random).order_by('-fecha').first()
            else:
                messages.warning(request, 'No se encontraron pacientes activos.')

    context = {
        'form': form,
        'paciente_random': paciente_random,
        'show_form': show_form,
        'datos_por_tipo': datos_por_tipo,
        'ultima_llamada': ultima_llamada,
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

    # Calcula totales por tipo de llamada
    total_por_tipo = {tipo.nombre: llamadas.filter(tipo=tipo).count() for tipo in tipos_llamadas}

    context = {
        'usuarios': usuarios,
        'tipos_llamadas': tipos_llamadas,
        'total_general': total_general,
        'total_por_tipo': total_por_tipo,
    }

    return render(request, template_name, context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def cargar_pacientes(request):
    if request.method == 'POST':
        # Si el formulario de carga masiva es enviado
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                return JsonResponse({'error': "El archivo no es un CSV."}, status=400)

            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)  # Saltar la cabecera

            for row_number, column in enumerate(csv.reader(io_string, delimiter=',', quotechar='"')):
                _, created = Paciente.objects.update_or_create(
                    rut=column[2],
                    defaults={
                        'nombre': column[0],
                        'apellido': column[1],
                        'numero_telefono': column[3],
                        # Asegúrese de que el campo 'is_active' se maneja correctamente según su modelo.
                        'is_active': column[4].strip().lower() in ['true', '1', 't', 'yes', 'y', 'si', 's']
                    }
                )
            return JsonResponse({'success': "Archivo CSV procesado correctamente."})

        # Si el formulario para agregar un paciente individual es enviado
        else:
            paciente_form = PacienteForm(request.POST)
            if paciente_form.is_valid():
                paciente_form.save()
                return JsonResponse({'success': "Paciente cargado correctamente."})
            else:
                return JsonResponse({'error': "Error al cargar el paciente. Verifique los datos."}, status=400)

    # Si no es un POST, se muestra el formulario normalmente
    else:
        paciente_form = PacienteForm()
        return render(request, "supervisor/cargar_pacientes.html", {'paciente_form': paciente_form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def gestionar_tipos_llamada(request):
    tipo_llamada_form = TipoLlamadaForm()
    cambiar_estado_form = CambiarEstadoTipoLlamadaForm()

    if request.method == 'POST':
        if 'nombre' in request.POST:
            tipo_llamada_form = TipoLlamadaForm(request.POST)
            if tipo_llamada_form.is_valid():
                tipo_llamada_form.save()
                messages.success(request, 'Tipo de llamada añadido o actualizado con éxito.')
        else:
            cambiar_estado_form = CambiarEstadoTipoLlamadaForm(request.POST)
            if cambiar_estado_form.is_valid():
                pk = request.POST.get('pk')  # Obtenemos 'pk' del POST
                estado = cambiar_estado_form.cleaned_data['estado']
                tipo_llamada = get_object_or_404(TipoLlamada, pk=pk)
                tipo_llamada.activo = estado
                tipo_llamada.save()

    tipos_llamada = TipoLlamada.objects.all()

    return render(request, 'supervisor/gestionar_tipos_llamada.html', {
        'tipo_llamada_form': tipo_llamada_form,
        'cambiar_estado_form': cambiar_estado_form,
        'tipos_llamada': tipos_llamada
    })

def cargar_paciente_manual(request):
    template = "supervisor/cargar_pacientes.html"

