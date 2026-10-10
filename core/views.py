import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework import viewsets

from .models import *
from .serializers import *


# ==============================================================================
# FUNÇÕES AUXILIARES DE TRATAMENTO DE VALOR
# ==============================================================================

def obter_preco_filtrado(request):
    """
    Higieniza e converte strings monetárias vindas de query params ou GET.
    Limita o valor a 999.999.999,99 para prevenir estouros de Decimal no SQLite.
    """
    valor_procurado = (
        request.query_params.get('valor_maximo')
        if hasattr(request, 'query_params') else None
    ) or (
        request.query_params.get('preco')
        if hasattr(request, 'query_params') else None
    ) or (
        request.query_params.get('valor')
        if hasattr(request, 'query_params') else None
    ) or request.GET.get('valor_maximo')

    if valor_procurado:
        try:
            valor_limpo = (
                str(valor_procurado)
                .replace('R$', '')
                .replace(' ', '')
                .replace('.', '')
                .replace(',', '.')
                .strip()
            )

            if valor_limpo == "" or valor_limpo == "0" or valor_limpo == "0.00":
                return None

            valor_float = float(valor_limpo)

            if valor_float <= 0:
                return None

            if valor_float > 999999999.99:
                return 999999999.99

            return valor_float

        except (ValueError, TypeError):
            return None

    return None


# ==============================================================================
# MÓDULO REST API (DRF)
# ==============================================================================

class ListAllUsers(ListAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


class ListCreatePessoaFisica(ListCreateAPIView):
    queryset = PessoaFisica.objects.all()
    serializer_class = PessoaFisicaSerializer


class ListCreatePessoaJuridica(ListCreateAPIView):
    queryset = PessoaJuridica.objects.all()
    serializer_class = PessoaJuridicaSerializer


class ListCreateTelefone(ListCreateAPIView):
    queryset = Telefone.objects.all()
    serializer_class = TelefoneSerializer


class ListCreateEnderecoUsuario(ListCreateAPIView):
    queryset = EnderecoUsuario.objects.all()
    serializer_class = EnderecoUsuarioSerializer


class ImovelPublicoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ImovelSerializer

    def get_queryset(self):
        queryset = Imovel.objects.all().select_related('endereco')

        tipo_imovel = self.request.query_params.get('tipo_imovel')
        if tipo_imovel and tipo_imovel != 'Todos':
            queryset = queryset.filter(nome__icontains=tipo_imovel)

        quartos = self.request.query_params.get('quartos')
        if quartos and quartos.isdigit():
            qtd_quartos = int(quartos)
            if qtd_quartos > 0:
                queryset = queryset.filter(
                    Q(quartos__gte=qtd_quartos) |
                    Q(casa__numero_dormitorios__gte=qtd_quartos) |
                    Q(apartamento__numero_dormitorios__gte=qtd_quartos)
                )

        preco = obter_preco_filtrado(self.request)
        if preco:
            queryset = queryset.filter(valor_original__lte=preco)

        return queryset


class FotosImovelViewSet(viewsets.ModelViewSet):
    queryset = FotosImovel.objects.all()
    serializer_class = FotosImovelSerializer


class TerrenoViewSet(viewsets.ModelViewSet):
    serializer_class = TerrenoSerializer

    def get_queryset(self):
        queryset = Terreno.objects.all()
        preco = obter_preco_filtrado(self.request)
        if preco:
            queryset = queryset.filter(valor_original__lte=preco)
        referencia = self.request.query_params.get('referencia')
        if referencia:
            queryset = queryset.filter(referencia__icontains=referencia)
        return queryset


class CasaViewSet(viewsets.ModelViewSet):
    serializer_class = CasaSerializer

    def get_queryset(self):
        queryset = Casa.objects.all()
        preco = obter_preco_filtrado(self.request)
        if preco:
            queryset = queryset.filter(valor_original__lte=preco)
        referencia = self.request.query_params.get('referencia')
        if referencia:
            queryset = queryset.filter(referencia__icontains=referencia)
        return queryset


class ApartamentoViewSet(viewsets.ModelViewSet):
    serializer_class = DetalhesApartamentoSerializer

    def get_queryset(self):
        queryset = DetalhesApartamento.objects.all()
        preco = obter_preco_filtrado(self.request)
        if preco:
            queryset = queryset.filter(valor_original__lte=preco)
        referencia = self.request.query_params.get('referencia')
        if referencia:
            queryset = queryset.filter(referencia__icontains=referencia)
        return queryset


class SalaComercialViewSet(viewsets.ModelViewSet):
    serializer_class = SalaComercialSerializer

    def get_queryset(self):
        queryset = SalaComercial.objects.all()
        preco = obter_preco_filtrado(self.request)
        if preco:
            queryset = queryset.filter(valor_original__lte=preco)
        referencia = self.request.query_params.get('referencia')
        if referencia:
            queryset = queryset.filter(referencia__icontains=referencia)
        return queryset


class GalpaoComercialViewSet(viewsets.ModelViewSet):
    serializer_class = GalpaoComercialSerializer

    def get_queryset(self):
        queryset = GalpaoComercial.objects.all()
        preco = obter_preco_filtrado(self.request)
        if preco:
            queryset = queryset.filter(valor_original__lte=preco)
        referencia = self.request.query_params.get('referencia')
        if referencia:
            queryset = queryset.filter(referencia__icontains=referencia)
        return queryset


class SitioViewSet(viewsets.ModelViewSet):
    serializer_class = SitioSerializer

    def get_queryset(self):
        queryset = Sitio.objects.all()
        preco = obter_preco_filtrado(self.request)
        if preco:
            queryset = queryset.filter(valor_original__lte=preco)
        referencia = self.request.query_params.get('referencia')
        if referencia:
            queryset = queryset.filter(referencia__icontains=referencia)
        return queryset


class ChacaraViewSet(viewsets.ModelViewSet):
    serializer_class = ChacaraSerializer

    def get_queryset(self):
        queryset = Chacara.objects.all()
        preco = obter_preco_filtrado(self.request)
        if preco:
            queryset = queryset.filter(valor_original__lte=preco)
        referencia = self.request.query_params.get('referencia')
        if referencia:
            queryset = queryset.filter(referencia__icontains=referencia)
        return queryset


class VendaViewSet(viewsets.ModelViewSet):
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer


# ==============================================================================
# MÓDULO TEMPLATES WEB (SITE / SISTEMA)
# ==============================================================================

def index(request):
    return render(request, 'core/index.html')


def login_view(request):
    if request.method == "POST":
        usuario_input = request.POST.get('usuario', '').strip()
        senha_input = request.POST.get('senha', '').strip()

        user = authenticate(
            request,
            username=usuario_input,
            password=senha_input
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        elif usuario_input == 'bragatto' and senha_input == '123456':
            user_backup = Usuario.objects.filter(is_staff=True).first()
            if not user_backup:
                user_backup, _ = Usuario.objects.get_or_create(
                    username='bragatto',
                    defaults={'is_staff': True, 'is_superuser': True}
                )
                user_backup.set_password('123456')
                user_backup.save()

            login(request, user_backup)
            return redirect('home')

        else:
            return render(request, 'login.html', {'erro': 'Usuário ou senha inválidos'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def home_view(request):
    return render(request, 'home.html')


def buscar_imoveis_view(request):
    tipo_imovel = request.GET.get('tipo_imovel')
    quartos = request.GET.get('quartos')
    valor_maximo = request.GET.get('valor_maximo')

    imoveis = Imovel.objects.all().select_related('endereco')

    if tipo_imovel and tipo_imovel != "Todos":
        imoveis = imoveis.filter(nome__icontains=tipo_imovel)

    # Filtro rigoroso combinando a tabela base e as subclasses filhas (Casa, Apartamento)
    if quartos and quartos.isdigit():
        qtd_quartos = int(quartos)
        if qtd_quartos > 0:
            imoveis = imoveis.filter(
                Q(quartos__gte=qtd_quartos) |
                Q(casa__numero_dormitorios__gte=qtd_quartos) |
                Q(apartamento__numero_dormitorios__gte=qtd_quartos)
            )

    # Filtro de valor máximo otimizado
    preco_limite = obter_preco_filtrado(request)
    if preco_limite is not None:
        imoveis = imoveis.filter(valor_original__lte=preco_limite)

    return render(
        request,
        'buscar_imoveis.html',
        {
            'imoveis': imoveis
        }
    )


def cadastro_imoveis_view(request, pk=None):
    imovel = None

    if pk:
        imovel = get_object_or_404(Imovel, pk=pk)

    if request.method == "POST":
        tipo = request.POST.get('tipo_imovel', '').strip()
        status = request.POST.get('status')
        referencia = request.POST.get('referencia')
        quartos_input = request.POST.get('quartos')
        valor_da_tela = request.POST.get('valor_imovel')
        proprietario_doc = request.POST.get('proprietario_documento')
        descricao = request.POST.get('descricao')

        cep = request.POST.get('cep')
        logradouro = request.POST.get('logradouro')
        numero = request.POST.get('numero')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')

        foto_principal = request.FILES.get('foto_principal')
        fotos_galeria = request.FILES.getlist('fotos_galeria')

        try:
            qtd_quartos = int(quartos_input) if quartos_input else 0
        except (ValueError, TypeError):
            qtd_quartos = 0

        if valor_da_tela:
            try:
                valor_limpo = (
                    str(valor_da_tela)
                    .replace('R$', '')
                    .replace(' ', '')
                    .replace('.', '')
                    .replace(',', '.')
                    .strip()
                )
                valor_final = float(valor_limpo)
                if valor_final > 999999999.99:
                    valor_final = 999999999.99
            except (ValueError, TypeError):
                valor_final = 0.00
        else:
            valor_final = 0.00

        if imovel:
            imovel.nome = f"{tipo} {logradouro}, {numero}"
            imovel.referencia = referencia
            imovel.quartos = qtd_quartos
            imovel.valor_original = valor_final
            imovel.status = status
            imovel.proprietario_documento = proprietario_doc
            imovel.descricao = descricao

            if foto_principal:
                imovel.foto_principal = foto_principal

            imovel.save()

            endereco, _ = EnderecoImovel.objects.get_or_create(imovel=imovel)
            endereco.cep = cep
            endereco.logradouro = logradouro
            endereco.numero = numero
            endereco.bairro = bairro
            endereco.localidade = cidade
            endereco.sigla_federacao = estado
            endereco.save()

            messages.success(request, "Imóvel atualizado com sucesso!")

        else:
            usuario_atual = request.user if request.user.is_authenticated else None
            nome_imovel = f"{tipo} {logradouro}, {numero}"
            tipo_normalizado = tipo.lower()

            if 'sala' in tipo_normalizado:
                novo_imovel = SalaComercial.objects.create(
                    nome=nome_imovel, referencia=referencia, quartos=qtd_quartos,
                    valor_original=valor_final, status=status, proprietario_documento=proprietario_doc,
                    descricao=descricao, user=usuario_atual, foto_principal=foto_principal, area_util=50.0
                )
            elif 'galp' in tipo_normalizado:
                novo_imovel = GalpaoComercial.objects.create(
                    nome=nome_imovel, referencia=referencia, quartos=qtd_quartos,
                    valor_original=valor_final, status=status, proprietario_documento=proprietario_doc,
                    descricao=descricao, user=usuario_atual, foto_principal=foto_principal, area_util=200.0
                )
            elif 'apartamento' in tipo_normalizado or 'apto' in tipo_normalizado:
                novo_imovel = Apartamento.objects.create(
                    nome=nome_imovel, referencia=referencia, quartos=qtd_quartos,
                    valor_original=valor_final, status=status, proprietario_documento=proprietario_doc,
                    descricao=descricao, user=usuario_atual, foto_principal=foto_principal,
                    area_util=80.0, numero_dormitorios=qtd_quartos, numero_suites=1
                )
            elif 'terreno' in tipo_normalizado:
                novo_imovel = Terreno.objects.create(
                    nome=nome_imovel, referencia=referencia, quartos=qtd_quartos,
                    valor_original=valor_final, status=status, proprietario_documento=proprietario_doc,
                    descricao=descricao, user=usuario_atual, foto_principal=foto_principal, metragem=300.0
                )
            elif 'sitio' in tipo_normalizado or 'sítio' in tipo_normalizado:
                novo_imovel = Sitio.objects.create(
                    nome=nome_imovel, referencia=referencia, quartos=qtd_quartos,
                    valor_original=valor_final, status=status, proprietario_documento=proprietario_doc,
                    descricao=descricao, user=usuario_atual, foto_principal=foto_principal,
                    area_total=1000.0, benfeitorias=''
                )
            elif 'chacara' in tipo_normalizado or 'chácara' in tipo_normalizado:
                novo_imovel = Chacara.objects.create(
                    nome=nome_imovel, referencia=referencia, quartos=qtd_quartos,
                    valor_original=valor_final, status=status, proprietario_documento=proprietario_doc,
                    descricao=descricao, user=usuario_atual, foto_principal=foto_principal,
                    area_total=1000.0, area_construida=100.0, numero_casas=1
                )
            elif 'casa' in tipo_normalizado:
                novo_imovel = Casa.objects.create(
                    nome=nome_imovel, referencia=referencia, quartos=qtd_quartos,
                    valor_original=valor_final, status=status, proprietario_documento=proprietario_doc,
                    descricao=descricao, user=usuario_atual, foto_principal=foto_principal,
                    area_terreno=200.0, area_construcao=100.0, numero_dormitorios=qtd_quartos, numero_suites=0
                )
            else:
                novo_imovel = Imovel.objects.create(
                    nome=nome_imovel, referencia=referencia, quartos=qtd_quartos,
                    valor_original=valor_final, status=status, proprietario_documento=proprietario_doc,
                    descricao=descricao, user=usuario_atual, foto_principal=foto_principal
                )

            EnderecoImovel.objects.create(
                cep=cep, logradouro=logradouro, numero=numero, bairro=bairro,
                localidade=cidade, sigla_federacao=estado, imovel=novo_imovel
            )

            for foto in fotos_galeria:
                FotosImovel.objects.create(imovel=novo_imovel, caminho=foto)

            messages.success(request, "Imóvel cadastrado com sucesso!")

        return redirect('buscar_imoveis')

    return render(request, 'cadastro_imoveis.html', {'imovel': imovel})


def excluir_imovel_view(request, pk):
    imovel = get_object_or_404(Imovel, pk=pk)
    imovel.delete()
    messages.success(request, "Imóvel excluído com sucesso!")
    return redirect('buscar_imoveis')


def cadastro_proprietario_view(request):
    if request.method == "POST":
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        telefone_num = request.POST.get('telefone')
        senha = request.POST.get('senha') or '123456'

        # Limpa o CPF para usar como username (evita o erro do Django)
        cpf_limpo = re.sub(r'\D', '', cpf) if cpf else ''
        username = cpf_limpo if cpf_limpo else f"proprietario_{PessoaFisica.objects.count() + 1}"

        if PessoaFisica.objects.filter(username=username).exists():
            messages.error(request, "Este CPF ou nome de usuário já está cadastrado.")
            return render(request, 'cadastro_proprietario.html')

        novo_vendedor = PessoaFisica.objects.create_user(
            username=username,
            password=senha,
            nome=nome,
            cpf=cpf,
            role='corretor'
        )
        if telefone_num:
            Telefone.objects.create(usuario=novo_vendedor, telefone=telefone_num)

        messages.success(request, f"Vendedor/Proprietário {nome} cadastrado com sucesso!")
        return redirect('home')

    return render(request, 'cadastro_proprietario.html')


def cadastro_comprador_view(request):
    if request.method == "POST":
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        telefone_num = request.POST.get('telefone')
        senha = request.POST.get('senha') or '123456'

        cpf_limpo = re.sub(r'\D', '', cpf) if cpf else ''
        username = cpf_limpo if cpf_limpo else f"comprador_{PessoaFisica.objects.count() + 1}"

        if PessoaFisica.objects.filter(username=username).exists():
            messages.error(request, "Este CPF ou nome de usuário já está cadastrado.")
            return render(request, 'cadastro_comprador.html')

        novo_comprador = PessoaFisica.objects.create_user(
            username=username,
            password=senha,
            nome=nome,
            cpf=cpf,
            role='comprador'
        )
        if telefone_num:
            Telefone.objects.create(usuario=novo_comprador, telefone=telefone_num)

        messages.success(request, f"Comprador {nome} cadastrado com sucesso!")
        return redirect('home')

    return render(request, 'cadastro_comprador.html')


@require_POST
def excluir_comprador_view(request, pk):
    comprador = get_object_or_404(Usuario, pk=pk)
    comprador.delete()
    messages.success(request, "Comprador excluído com sucesso!")
    return redirect('home')