from .models import Llamada, TipoLlamada, Paciente
from .forms import LlamadaForm, TipoLlamadaForm, CambiarEstadoTipoLlamadaForm, PacienteForm
from django.utils.timezone import datetime, timedelta
from django.db.models import Count
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required, user_passes_test
import csv, io
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import CustomUser
from django.contrib import messages
from django.db.models import Q


# Vista para registrar llamadas, requiere autenticación del usuario.
@login_required()
def registrar_llamada(request):
    paciente_random = None
    show_form = False
    form = LlamadaForm()
    ultima_llamada = None

    # Obtenemos  todas las llamadas del usuario actual
    llamadas = Llamada.objects.filter(usuario=request.user)

    # Obtención de tipos de llamada activos
    tipos_llamada_activos = TipoLlamada.objects.filter(activo=True)

    # Diccionario para almacenar datos por tipo de llamada
    datos_por_tipo = {}

    # Ciclo for para iterar tipos de llamada activos
    for tipo in tipos_llamada_activos:
        conteo = llamadas.filter(tipo=tipo).count()
        datos_por_tipo[tipo.nombre] = {'conteo': conteo}


    if request.method == 'POST':
        if 'generar_llamada' in request.POST:
            # Generar un paciente aleatorio activo
            paciente_random = Paciente.objects.filter(is_active=True).order_by('?').first()
            if paciente_random:
                show_form = True
            else:
                messages.warning(request, 'No se encontraron pacientes activos.')
        elif 'buscar_paciente' in request.POST:
            # Buscar paciente por RUT ingresado en el formulario
            paciente_rut = request.POST.get('buscar_rut')
            try:
                paciente = Paciente.objects.get(rut=paciente_rut, is_active=True)
                paciente_random = paciente
                show_form = True
                ultima_llamada = Llamada.objects.filter(paciente=paciente).order_by('-fecha').first()
            except Paciente.DoesNotExist:
                messages.warning(request, 'No se encontró un paciente activo con ese RUT.')
        else:
            form = LlamadaForm(request.POST)
            paciente_rut = request.POST.get('paciente_rut')
            paciente = Paciente.objects.get(rut=paciente_rut)

            # Validar el formulario y asegurarse de que se ha seleccionado un paciente
            if form.is_valid() and paciente:
                llamada = form.save(commit=False)
                llamada.usuario = request.user
                llamada.paciente = paciente
                llamada.save()

                # Desactivar al paciente si el tipo de llamada es "No volver a llamar"
                if llamada.tipo.nombre == 'No volver a llamar':
                    paciente.is_active = False
                    paciente.save()

                # Mensaje de éxito y redireccionamiento para nuevas llamadas
                messages.success(request, 'Llamada registrada con éxito.')
                return redirect('registrar_llamada')
            else:
                messages.error(request, 'Error al registrar la llamada. Asegúrese de haber seleccionado un paciente.')

    # Contexto para renderizar con datos necesarios
    context = {
        'form': form,
        'paciente_random': paciente_random,
        'show_form': show_form,
        'datos_por_tipo': datos_por_tipo,
        'ultima_llamada': ultima_llamada,
    }

    return render(request, 'llamadas/registrar_llamada.html', context)


@login_required
#permite el acceso solo a usuarios que esten marcados como "is_staff" en la base de datos
@user_passes_test(lambda u: u.is_staff)
def revisar_llamadas(request):
    template_name = 'supervisor/revisar_llamadas.html'

    # Obtener todos los tipos de llamadas
    tipos_llamadas = TipoLlamada.objects.all()

    # Obtener las fechas de inicio y fin desde los parámetros de la solicitud GET
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    # Filtrar llamadas por rango de fechas si se proporcionan
    if fecha_desde and fecha_hasta:
        fecha_desde = make_aware(datetime.strptime(fecha_desde, '%Y-%m-%d'))
        fecha_hasta = make_aware(datetime.strptime(fecha_hasta, '%Y-%m-%d'))
        fecha_hasta += timedelta(days=1) - timedelta(seconds=1)
        llamadas = Llamada.objects.filter(fecha__range=(fecha_desde, fecha_hasta))
    else:
        llamadas = Llamada.objects.all()

    # Obtener conteos de llamadas por usuario
    usuarios_conteos = llamadas.values('usuario__rut').annotate(total=Count('id')).order_by('-total')

    usuarios = []

    # Iterar a través de los usuarios y sus conteos
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

    # Calcular el total general de llamadas
    total_general = sum(usuario['total'] for usuario in usuarios)

    # Obtener el total de llamadas por tipo
    total_por_tipo = {tipo.nombre: llamadas.filter(tipo=tipo).count() for tipo in tipos_llamadas}

    # Contar las llamadas de tipo 'Cita' y calcular el porcentaje de éxito
    citas_count = llamadas.filter(tipo__nombre='Cita').count()
    porcentaje_exito = (citas_count / total_general * 100) if total_general > 0 else 0

    # Contexto para renderizar la página con datos necesarios
    context = {
        'usuarios': usuarios,
        'tipos_llamadas': tipos_llamadas,
        'total_general': total_general,
        'total_por_tipo': total_por_tipo,
        'porcentaje_exito': porcentaje_exito,
    }

    # Renderizar la página de revisión de llamadas
    return render(request, template_name, context)


def cargar_pacientes(request):
    # Si se recibe una solicitud POST
    if request.method == 'POST':
        # Si se adjunta un archivo CSV
        if 'csv_file' in request.FILES:
            # Obtener el archivo CSV
            csv_file = request.FILES['csv_file']

            # Verificar si el archivo tiene extensión CSV
            if not csv_file.name.endswith('.csv'):
                return JsonResponse({'error': "El archivo no es un CSV."}, status=400)

            # Leer y decodificar el contenido del archivo CSV
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)

            # Inicializar lista para usuarios duplicados
            duplicate_users = []

            # Iterar a través de las filas del CSV
            for row_number, column in enumerate(csv.reader(io_string, delimiter=',', quotechar='"')):
                rut = column[2]
                telefono = column[3]

                # Verificar si el usuario ya existe por RUT o número de teléfono
                if Paciente.objects.filter(Q(rut=rut) | Q(numero_telefono=telefono)).exists():
                    duplicate_users.append({'row_number': row_number + 2, 'rut': rut, 'telefono': telefono})
                else:
                    # Actualizar o crear nuevo paciente en la base de datos
                    _, created = Paciente.objects.update_or_create(
                        rut=rut,
                        defaults={
                            'nombre': column[0],
                            'apellido': column[1],
                            'numero_telefono': telefono,
                            'is_active': column[4].strip().lower() in ['true', '1', 't', 'yes', 'y', 'si', 's']
                        }
                    )

            # Devolver respuesta JSON con información sobre usuarios duplicados, si los hay
            if duplicate_users:
                return JsonResponse({
                    'error': "Algunos usuarios ya existen en la base de datos.",
                    'duplicate_users': duplicate_users
                }, status=400)
            else:
                return JsonResponse({'success': "Archivo CSV procesado correctamente."})

        # Si no se adjunta un archivo CSV, procesar formulario de paciente
        else:
            paciente_form = PacienteForm(request.POST)
            if paciente_form.is_valid():
                paciente_form.save()
                return JsonResponse({'success': "Paciente cargado correctamente."})
            else:
                return JsonResponse({'error': "Error al cargar el paciente. Verifique los datos."}, status=400)

    # Si la solicitud no es POST, renderizar página con formulario vacío
    else:
        paciente_form = PacienteForm()
        return render(request, "supervisor/cargar_pacientes.html", {'paciente_form': paciente_form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def gestionar_tipos_llamada(request):
    # Inicializar formularios y obtener tipos de llamada existentes
    tipo_llamada_form = TipoLlamadaForm()
    cambiar_estado_form = CambiarEstadoTipoLlamadaForm()

    # Procesar solicitud POST
    if request.method == 'POST':
        # Si se proporciona "nombre" en el POST, procesar formulario de tipo de llamada
        if 'nombre' in request.POST:
            tipo_llamada_form = TipoLlamadaForm(request.POST)
            if tipo_llamada_form.is_valid():
                tipo_llamada_form.save()
                messages.success(request, 'Tipo de llamada añadido o actualizado con éxito.')
        # Si no se proporciona "nombre", procesar formulario para cambiar el estado de un tipo de llamada
        else:
            cambiar_estado_form = CambiarEstadoTipoLlamadaForm(request.POST)
            if cambiar_estado_form.is_valid():
                # Obtener "pk" del POST
                pk = request.POST.get('pk')
                # Obtener el estado del formulario
                estado = cambiar_estado_form.cleaned_data['estado']
                # Obtener el objeto TipoLlamada correspondiente
                tipo_llamada = get_object_or_404(TipoLlamada, pk=pk)
                # Actualizar el estado del tipo de llamada y guardar cambios
                tipo_llamada.activo = estado
                tipo_llamada.save()

    # Obtener todos los tipos de llamada existentes
    tipos_llamada = TipoLlamada.objects.all()

    # Renderizar página con formularios y tipos de llamada
    return render(request, 'supervisor/gestionar_tipos_llamada.html', {
        'tipo_llamada_form': tipo_llamada_form,
        'cambiar_estado_form': cambiar_estado_form,
        'tipos_llamada': tipos_llamada
    })


@user_passes_test(lambda u: u.is_staff)
def pacientes_no_llamar(request):
    if request.method == 'POST':
        # Obtener el RUT del paciente del POST
        rut_paciente = request.POST.get('rut_paciente')
        # Obtener el objeto Paciente correspondiente o mostrar 404 si no existe
        paciente = get_object_or_404(Paciente, rut=rut_paciente)
        # Reactivar al paciente y guardar cambios
        paciente.is_active = True
        paciente.save()
        # Mostrar mensaje de éxito y redirigir para evitar reenvío del formulario
        messages.success(request, f'El paciente {paciente.nombre} ha sido reactivado.')
        return redirect('pacientes_no_llamar')

    # Obtener todos los pacientes inactivos
    pacientes_inactivos = Paciente.objects.filter(is_active=False)

    # Renderizar página con pacientes inactivos
    return render(request, 'supervisor/pacientes_no_llamar.html', {'pacientes_inactivos': pacientes_inactivos})


@login_required
@user_passes_test(lambda u: u.is_staff)
def gestion_usuarios(request):
    # Obtener todos los usuarios
    users = CustomUser.objects.all()

    # Procesar solicitud POST
    if request.method == 'POST':
        # Obtener el RUT del usuario del POST
        user_rut = request.POST.get('user_rut')
        # Obtener el objeto CustomUser correspondiente o mostrar 404 si no existe
        user = get_object_or_404(CustomUser, rut=user_rut)

        # Cambiar la contraseña si se envía el formulario correspondiente
        if 'change_password' in request.POST:
            new_password = request.POST.get('new_password')
            user.set_password(new_password)
            user.save()
            messages.success(request, f'Contraseña actualizada para {user.get_full_name()}.')

        # Cambiar el estado de activación si se envía el formulario correspondiente
        elif 'toggle_active' in request.POST:
            user.is_active = not user.is_active
            user.save()
            status = 'activado' if user.is_active else 'desactivado'
            messages.success(request, f'Usuario {user.get_full_name()} ha sido {status}.')

        # Cambiar los permisos de Supervisor si se envía el formulario correspondiente
        elif 'toggle_staff' in request.POST:
            user.is_staff = not user.is_staff
            user.save()
            status = 'agregados' if user.is_staff else 'quitados'
            messages.success(request, f'Permisos de Supervisor {status} para {user.get_full_name()}.')

    # Renderizar página con la lista de usuarios
    return render(request, 'supervisor/gestion_usuarios.html', {'users': users})