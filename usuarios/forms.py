# Formulario de registro de usuario
from django import forms
from .models import CustomUser

class RegistroForm(forms.ModelForm):
    # Campos adicionales para contraseña y fecha de nacimiento
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'type': 'date'}),
        label='Fecha de nacimiento'
    )

    class Meta:
        model = CustomUser
        fields = ('rut', 'fecha_nacimiento', 'nombre', 'apellido', 'email')

    # Validación para confirmar que las contraseñas coinciden
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden')

        return password2

    # Guardar la contraseña en formato hash y el usuario si se confirma el registro
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

        return user

# Formulario de inicio de sesión
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)