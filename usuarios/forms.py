from django import forms
from .models import CustomUser

class RegistroForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
    fecha_nacimiento = forms.DateField(

        widget=forms.DateInput(format='%d/%m/%Y', attrs={'type': 'date'}),
        label='Fecha de nacimiento'
    )

    class Meta:
        model = CustomUser
        fields = ('rut', 'fecha_nacimiento', 'nombre', 'apellido', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden')

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

        return user

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)