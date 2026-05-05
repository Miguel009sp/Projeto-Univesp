from django.db import models
from django.contrib.auth.models import AbstractUser


# nao e necessario colocar `email`e `senha`  pois o AbstractUser
# ja faz isso
# foto de perfil -> so salvamos o path da imagem
# nome -> pelo `username` nativo do abstract user ser unique por padrao,
# criar um campo nome e uma boa opcao
class Usuario(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer')
    )
    
    nome = models.CharField(max_length=255)
    foto = models.ImageField(upload_to='usuario/profile', max_length=255, null=True)
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

class EnderecoUsuario(models.Model):
    bairro = models.CharField(max_length=100)
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=9)
    localidade = models.CharField(max_length=100)
    sigla_federacao = models.CharField(max_length=2)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)

# imoveis
class EnderecoImovel(models.Model):
    bairro = models.CharField(max_length=100)
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=9)
    localidade = models.CharField(max_length=100)
    sigla_federacao = models.CharField(max_length=2)

class Imovel(models.Model):

    STATUS_CHOICES = (
        ('oculto', 'Oculto'),
        ('vendido', 'Vendido'),
        ('disponivel', 'Disponivel'),
    )

    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    foto_principal = models.CharField(max_length=255)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE) # representa o dono do imovel
    valor_original = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    endereco = models.ForeignKey(EnderecoImovel, on_delete=models.SET_NULL, null=True)
    
class FotosImovel(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE)
    caminho = models.ImageField(upload_to='imoveis/galeria', max_length=255)
    
class Terreno(Imovel):
    metragem = models.DecimalField(max_digits=10, decimal_places=2)

class Casa(Imovel):
    area_terreno = models.DecimalField(max_digits=10, decimal_places=2)
    area_construcao = models.DecimalField(max_digits=10, decimal_places=2)
    numero_dormitorios = models.IntegerField()
    numero_suites = models.IntegerField()

class Apartamento(Imovel):
    area_util = models.DecimalField(max_digits=10, decimal_places=2)
    numero_dormitorios = models.IntegerField()
    numero_suites = models.IntegerField()

class DetalhesApartamento(Apartamento):
    bloco = models.CharField(max_length=15)
    andar = models.CharField(max_length=15)

class SalaComercial(Imovel):
    area_util = models.DecimalField(max_digits=10, decimal_places=2)

class GalpaoComercial(Imovel):
    area_util = models.DecimalField(max_digits=10, decimal_places=2)

class Sitio(Imovel):
    area_total = models.DecimalField(max_digits=10, decimal_places=2)
    benfeitorias = models.TextField()

class Chacara(Imovel):
    area_total = models.DecimalField(max_digits=10, decimal_places=2)
    area_construida = models.DecimalField(max_digits=10, decimal_places=2)
    numero_casas = models.IntegerField()

# registro de venda
# a venda real nao pode ser feita por essa aplicacao por motivos
# de complexidade, lgpd e a necessidade de integracao com API de pagamentos
# confivavel. 
# essa tabela servira apenas para ter-se um historico de vendas realizadas.

# PROTECT: se houver exclusao da entidade referenciada, 
# o PROTECT impedira para poder manter o historico.
class Venda(models.Model):

    STATUS_VENDA = (
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
        ('executando', 'Executando')
    )

    imovel = models.ForeignKey(Imovel, on_delete=models.PROTECT)
    comprador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='comprador')
    vendedor = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='vendedor')
    preco_pedido = models.DecimalField(max_digits=12, decimal_places=2)
    preco_final = models.DecimalField(max_digits=12, decimal_places=2)
    data_publicacao = models.DateField(auto_now_add=True)
    data_fechamento = models.DateField(null=True)
    observacoes = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_VENDA)
    
