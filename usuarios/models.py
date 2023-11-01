from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, rut, fecha_nacimiento, nombre, apellido, email, password=None):
        if not rut:
            raise ValueError('El RUT es obligatorio')
        email = self.normalize_email(email)
        user = self.model(rut=rut, fecha_nacimiento=fecha_nacimiento, nombre=nombre, apellido=apellido, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, fecha_nacimiento, nombre, apellido, email, password):
        user = self.create_user(rut, fecha_nacimiento, nombre, apellido, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    rut = models.CharField(max_length=12, primary_key=True, unique=True)
    fecha_nacimiento = models.DateField()
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['fecha_nacimiento', 'nombre', 'apellido', 'email']

    def __str__(self):
        return self.rut
