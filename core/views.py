from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from .models import *
from .serializers import *

# lista todos os usarios (PEssoa Fisica e Pessoa Jurica, 
# mas sem suas informacoes especificas)
class ListAllUsers(ListAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

# Lista ou cria pessoa fisica
class ListCreatePessoaFisica(ListCreateAPIView):
    queryset = PessoaFisica.objects.all()
    serializer_class = PessoaFisicaSerializer
    
# Lista ou cria pessoa juridica
class ListCreatePessoaJuridica(ListCreateAPIView):
    queryset = PessoaJuridica.objects.all()
    serializer_class = PessoaJuridicaSerializer

# Lista todos os telefones dos usuarios (sem filtro)
# Registra os telefones de um usuario
class ListCreateTelefone(ListCreateAPIView):
    queryset = Telefone.objects.all()
    serializer_class = TelefoneSerializer

# Lista todos os enderecos dos usuarios (sem filtro)
# Registra os enderecos de um usuario
class ListCreateEnderecoUsuario(ListCreateAPIView):
    queryset = EnderecoUsuario.objects.all()
    serializer_class = EnderecoUsuarioSerializer

# Imovel
class ImovelViewSet(viewsets.ViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer


    
    

        
