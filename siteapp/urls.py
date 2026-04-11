from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
     path('home/', views.home_view, name='home'),
    path('buscar-imoveis/', views.buscar_imoveis_view, name='buscar_imoveis'),
    path('cadastro-proprietario/', views.cadastro_proprietario_view, name= 'cadastro_proprietario'),
    path('cadastro-imoveis/', views.cadastro_imoveis_view, name='cadastro_imoveis'),
    path('cadastro-comprador/', views.cadastro_comprador_view, name='cadastro_comprador'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.login_view, name='login'),

]
