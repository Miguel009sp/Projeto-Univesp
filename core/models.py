from django.db import models
from django.contrib.auth.models import AbstractUser

# nao e necessario colocar `email`
# nem `senha` pois o AbstractUser
# ja faz isso
# foto de perfil -> so salvamos o path da imagem
class Usuario(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer')
    )
    
    nome = models.CharField(max_length=255)
    foto = models.CharField(max_length=255, null=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)

class PessoaFisica(Usuario):
    cpf = models.CharField(max_length=14, unique=True)
    rg = models.CharField(max_length=20)

class PessoaJuridica(Usuario):
    cnpj = models.CharField(max_length=18, unique=True)
    nome_empresa = models.CharField(max_length=255)
    nome_comercial = models.CharField(max_length=255)

class Telefone(models.Model):
    telefone = models.CharField(max_length=20)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='telefones')

class Endereco(models.Model):
    bairro = models.CharField(max_length=100)
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=9)
    localidade = models.CharField(max_length=100)
    sigla_federacao = models.CharField(max_length=2)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    
