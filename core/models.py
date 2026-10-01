from django.db import models
from django.contrib.auth.models import AbstractUser

# --- USUÁRIOS ---

class Usuario(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('corretor', 'Corretor / Vendedor'),
        ('proprietario', 'Proprietário'),
        ('comprador', 'Comprador'),
    )
    
    nome = models.CharField(max_length=255)
    foto = models.ImageField(upload_to='usuario/profile', max_length=255, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='comprador')

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


# --- IMÓVEIS ---

class Imovel(models.Model):
    STATUS_CHOICES = (
        ('disponivel', 'Disponível'),
        ('indisponivel', 'Indisponível'),
        ('vendido', 'Vendido'),
        ('oculto', 'Oculto'),
    )

    nome = models.CharField(max_length=255)
    referencia = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número de Referência")
    descricao = models.TextField(blank=True, null=True)
    foto_principal = models.ImageField(upload_to='imovel/main_pic', max_length=255, null=True, blank=True)
    
    # Representa o dono do imóvel (Usuário do sistema)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE) 
    
    # Campo para salvar o CPF/CNPJ digitado no cadastro/edição
    proprietario_documento = models.CharField(max_length=18, null=True, blank=True)
    
    valor_original = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='disponivel')

    def __str__(self):
        return self.nome

class EnderecoImovel(models.Model):
    bairro = models.CharField(max_length=100)
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=9)
    localidade = models.CharField(max_length=100)
    sigla_federacao = models.CharField(max_length=2)
    imovel = models.OneToOneField(Imovel, on_delete=models.CASCADE, related_name="endereco")
    
class FotosImovel(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name="galeria")
    caminho = models.ImageField(upload_to='imoveis/galeria', max_length=255)

# Especializações do Imóvel

class Terreno(Imovel):
    metragem = models.DecimalField(max_digits=10, decimal_places=2)

class Casa(Imovel):
    area_terreno = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    area_construcao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    numero_dormitorios = models.IntegerField(default=0)
    numero_suites = models.IntegerField(default=0)

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


# --- REGISTRO DE VENDA ---

class Venda(models.Model):
    STATUS_VENDA = (
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
        ('executando', 'Executando')
    )

    imovel = models.ForeignKey(Imovel, on_delete=models.PROTECT)
    comprador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='compras')
    vendedor = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='vendas')
    preco_pedido = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    preco_final = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    data_publicacao = models.DateField(auto_now_add=True)
    data_fechamento = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_VENDA, default='executando')
    