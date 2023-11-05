from django import forms
from .models import Llamada, TipoLlamada

class LlamadaForm(forms.ModelForm):
    class Meta:
        model = Llamada
        fields = ['tipo', 'comentario']

class FilterForm(forms.Form):
    desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))


