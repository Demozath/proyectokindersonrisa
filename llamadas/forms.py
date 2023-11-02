from django import forms
from .models import Llamada, TipoLlamada

class LlamadaForm(forms.ModelForm):
    class Meta:
        model = Llamada
        fields = ['tipo', 'comentario']

