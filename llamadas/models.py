from django.db import models
from usuarios.models import CustomUser

class TipoLlamada(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Llamada(models.Model):
    tipo = models.ForeignKey('TipoLlamada', on_delete=models.CASCADE)
    comentario = models.TextField()
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.usuario.rut} - {self.tipo.nombre}'

class Paciente(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    rut = models.CharField(max_length=12, primary_key=True, unique=True)
    numero_telefono = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

