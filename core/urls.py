from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'imoveis', viewset=ImovelViewSet)

urlpatterns = [   
    path('', include(router.urls)),

    # usuario comum (sem admin) url (GET e POST)
    path('pessoa-fisica', ListCreatePessoaFisica.as_view()),
    path('pessoa-juridica', ListCreatePessoaJuridica.as_view()),

    # todos os usuarios (lista sem informacao de pessoa fisica ou juridica - GET)
    path('usuarios', ListAllUsers.as_view()),
    path('telefone', ListCreateTelefone.as_view()),
    path('endereco-usuario', ListCreateEnderecoUsuario.as_view()),
]
