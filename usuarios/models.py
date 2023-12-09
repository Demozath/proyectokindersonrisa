from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, rut, fecha_nacimiento, nombre, apellido, email, password=None):
        if not rut:
            raise ValueError('El RUT es obligatorio')
        email = self.normalize_email(email)
        user = self.model(rut=rut, fecha_nacimiento=fecha_nacimiento, nombre=nombre, apellido=apellido, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
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

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"

    def get_short_name(self):
        return self.nombre

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

