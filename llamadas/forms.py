from django import forms
from .models import Llamada, TipoLlamada, Paciente

class LlamadaForm(forms.ModelForm):
    class Meta:
        model = Llamada
        fields = ['tipo']

class FilterForm(forms.Form):
    desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class TipoLlamadaForm(forms.ModelForm):
    class Meta:
        model = TipoLlamada
        fields = ['nombre', 'activo']

class CambiarEstadoTipoLlamadaForm(forms.Form):
    estado = forms.BooleanField(required=False)


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'rut', 'numero_telefono']

    def clean_rut(self):
        rut = self.cleaned_data['rut']
        if Paciente.objects.filter(rut=rut).exists():
            raise forms.ValidationError('Un paciente con este RUT ya existe.')
        return rut