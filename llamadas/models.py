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

    def __str__(self):
        return f'{self.usuario.rut} - {self.tipo.nombre}'
