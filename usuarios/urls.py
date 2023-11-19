from django.urls import path
from .views import registro, login_view, menu_principal
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('registro/', registro, name='registro'),
    path('login/', login_view, name='login'),
    path('menu_principal/', menu_principal, name='menu_principal'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

]
