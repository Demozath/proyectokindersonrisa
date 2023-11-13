from django.urls import path
from .views import registro, login_view, menu_principal

urlpatterns = [
    path('registro/', registro, name='registro'),
    path('login/', login_view, name='login'),
    path('menu_principal/', menu_principal, name='menu_principal')

]
