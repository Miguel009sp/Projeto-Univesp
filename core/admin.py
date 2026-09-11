from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, PessoaFisica, PessoaJuridica, Telefone, EnderecoUsuario,
    Imovel, EnderecoImovel, FotosImovel, Terreno, Casa, Apartamento,
    DetalhesApartamento, SalaComercial, GalpaoComercial, Sitio, Chacara, Venda
)

# 1. Configurações inline (Fotos e Endereço no Imóvel e Usuário)
class FotosImovelInline(admin.TabularInline):
    model = FotosImovel
    fk_name = 'imovel'
    extra = 1

class EnderecoImovelInline(admin.StackedInline):
    model = EnderecoImovel
    can_delete = False

class TelefoneInline(admin.TabularInline):
    model = Telefone
    extra = 1

class EnderecoUsuarioInline(admin.StackedInline):
    model = EnderecoUsuario
    extra = 1


# 2. Configuração do Admin de Usuários e Perfis
@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informações de Perfil', {'fields': ('nome', 'foto', 'role')}),
    )
    list_display = ('id', 'username', 'email', 'nome', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'nome')

@admin.register(PessoaFisica)
class PessoaFisicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'nome', 'cpf', 'role')
    search_fields = ('nome', 'cpf', 'username')
    inlines = [TelefoneInline, EnderecoUsuarioInline]

@admin.register(PessoaJuridica)
class PessoaJuridicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'nome_empresa', 'cnpj', 'role')
    search_fields = ('nome_empresa', 'cnpj', 'username')
    inlines = [TelefoneInline, EnderecoUsuarioInline]

@admin.register(Telefone)
class TelefoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'telefone')

@admin.register(EnderecoUsuario)
class EnderecoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'logradouro', 'bairro', 'localidade', 'sigla_federacao')


# 3. Configuração do Admin de Imóveis (Base e Tipologias)
class ImovelAdminBase(admin.ModelAdmin):
    list_display = ('id', 'nome', 'user', 'proprietario_documento', 'valor_original', 'status')
    list_editable = ('user', 'status')  # Permite alterar o dono/comprador e status na propria tabela
    list_filter = ('status',)
    search_fields = ('nome', 'descricao', 'proprietario_documento', 'referencia')
    inlines = [EnderecoImovelInline, FotosImovelInline]

@admin.register(Imovel)
class ImovelAdmin(ImovelAdminBase):
    pass

@admin.register(Casa)
class CasaAdmin(ImovelAdminBase):
    pass

@admin.register(Apartamento)
class ApartamentoAdmin(ImovelAdminBase):
    pass

@admin.register(DetalhesApartamento)
class DetalhesApartamentoAdmin(ImovelAdminBase):
    pass

@admin.register(Terreno)
class TerrenoAdmin(ImovelAdminBase):
    pass

@admin.register(SalaComercial)
class SalaComercialAdmin(ImovelAdminBase):
    pass

@admin.register(GalpaoComercial)
class GalpaoComercialAdmin(ImovelAdminBase):
    pass

@admin.register(Sitio)
class SitioAdmin(ImovelAdminBase):
    pass

@admin.register(Chacara)
class ChacaraAdmin(ImovelAdminBase):
    pass

@admin.register(EnderecoImovel)
class EnderecoImovelAdmin(admin.ModelAdmin):
    list_display = ('id', 'imovel', 'logradouro', 'bairro', 'localidade', 'cep')

@admin.register(FotosImovel)
class FotosImovelAdmin(admin.ModelAdmin):
    list_display = ('id', 'imovel', 'caminho')


# 4. Histórico de Vendas
@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'imovel', 'comprador', 'vendedor', 'preco_final', 'status', 'data_fechamento')
    list_filter = ('status', 'data_fechamento')
    search_fields = ('imovel__nome', 'comprador__username', 'vendedor__username')
    
    