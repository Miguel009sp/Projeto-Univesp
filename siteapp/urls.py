from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Telas Principais
    path('home/', views.home_view, name='home'),
    path('buscar-imoveis/', views.buscar_imoveis_view, name='buscar_imoveis'),

    # Gestão de Imóveis (Cadastro, Edição e Exclusão)
    path('cadastro-imoveis/', views.cadastro_imoveis_view, name='cadastro_imoveis'),
    path('editar-imovel/<int:pk>/', views.cadastro_imoveis_view, name='editar_imovel'),
    path('excluir-imovel/<int:pk>/', views.excluir_imovel_view, name='excluir_imovel'),

    # Gestão de Compradores (Cadastro, Edição, Listagem e Exclusão)
    path('cadastro-comprador/', views.cadastro_comprador_view, name='cadastro_comprador'),
    path('editar-comprador/<int:pk>/', views.cadastro_comprador_view, name='editar_comprador'),
    path('compradores/', views.lista_compradores_view, name='lista_compradores'),
    path('excluir-comprador/<int:pk>/', views.excluir_comprador_view, name='excluir_comprador'),

    # Gestão de Proprietários
    path('cadastro-proprietario/', views.cadastro_proprietario_view, name='cadastro_proprietario'),
]