import re

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q

from core.models import (
    Usuario,
    PessoaFisica,
    Telefone,
    Imovel,
    Casa,
    Apartamento,
    Terreno,
    SalaComercial,
    GalpaoComercial,
    Sitio,
    Chacara,
    FotosImovel,
    EnderecoImovel
)

# ==============================================================================
# MÓDULO 1: AUTENTICAÇÃO E SESSÃO DO USUÁRIO
# ==============================================================================

def login_view(request):
    """
    Controla o acesso inicial realizando o login no Django.
    """
    if request.method == "POST":
        usuario_input = request.POST.get('usuario', '').strip()
        senha_input = request.POST.get('senha', '').strip()

        # Tenta autenticar no Django
        user = authenticate(
            request,
            username=usuario_input,
            password=senha_input
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        # Backup de desenvolvimento
        elif usuario_input == 'bragatto' and senha_input == '123456':
            user_backup = Usuario.objects.filter(is_staff=True).first()

            if not user_backup:
                user_backup, _ = Usuario.objects.get_or_create(
                    username='bragatto',
                    defaults={
                        'is_staff': True,
                        'is_superuser': True
                    }
                )

                user_backup.set_password('123456')
                user_backup.save()

            login(request, user_backup)
            return redirect('home')

        else:
            return render(
                request,
                'login.html',
                {'erro': 'Usuário ou senha inválidos'}
            )

    return render(request, 'login.html')

def logout_view(request):
    """
    Encerra a sessão ativa.
    """
    logout(request)
    return redirect('login')

def home_view(request):
    """
    Renderiza o Dashboard Administrativo.
    """
    return render(request, 'home.html')

# ==============================================================================
# MÓDULO 2: LOGÍSTICA E OPERAÇÕES DE IMÓVEIS
# ==============================================================================

def buscar_imoveis_view(request):
    """
    Painel de consulta de imóveis com filtros de tipo, quartos e valor máximo.
    """
    tipo_imovel = request.GET.get('tipo_imovel')
    quartos = request.GET.get('quartos')
    valor_maximo = request.GET.get('valor_maximo')

    imoveis = Imovel.objects.all().select_related('endereco')

    if tipo_imovel and tipo_imovel != "Todos":
        imoveis = imoveis.filter(
            nome__icontains=tipo_imovel
        )

    # Filtro robusto de quartos considerando a herança multi-tabela
    if quartos and quartos.isdigit():
        qtd_quartos = int(quartos)
        if qtd_quartos > 0:
            imoveis = imoveis.filter(
                Q(quartos__gte=qtd_quartos) |
                Q(casa__numero_dormitorios__gte=qtd_quartos) |
                Q(apartamento__numero_dormitorios__gte=qtd_quartos)
            )

    if valor_maximo:
        try:
            valor_limpo = (
                str(valor_maximo)
                .replace('R$', '')
                .replace(' ', '')
                .replace('.', '')
                .replace(',', '.')
                .strip()
            )

            if valor_limpo != "" and valor_limpo != "0" and valor_limpo != "0.00":
                preco_limite = float(valor_limpo)
                if preco_limite > 0:
                    imoveis = imoveis.filter(
                        valor_original__lte=preco_limite
                    )

        except (ValueError, TypeError):
            pass

    return render(
        request,
        'buscar_imoveis.html',
        {'imoveis': imoveis}
    )

def cadastro_imoveis_view(request, pk=None):
    """
    Controlador de criação e edição de imóveis.
    """

    imovel = None

    if pk:
        imovel = get_object_or_404(
            Imovel,
            pk=pk
        )

    if request.method == "POST":

        # ----------------------------------------------------------------------
        # DADOS BÁSICOS
        # ----------------------------------------------------------------------

        tipo = request.POST.get('tipo_imovel', '').strip()
        status = request.POST.get('status')
        referencia = request.POST.get('referencia')
        valor_da_tela = request.POST.get('valor_imovel')
        proprietario_doc = request.POST.get('proprietario_documento')
        descricao = request.POST.get('descricao')
        usuario_id = request.POST.get('usuario')

        # CAPTURA DO NÚMERO DE QUARTOS
        quartos_input = request.POST.get('quartos', 0)
        try:
            quartos_val = int(quartos_input) if quartos_input else 0
        except (ValueError, TypeError):
            quartos_val = 0

        # ----------------------------------------------------------------------
        # ENDEREÇO (Tratamento para evitar NULL em campos obrigatórios)
        # ----------------------------------------------------------------------

        cep = request.POST.get('cep', '') or ''
        logradouro = request.POST.get('logradouro', '') or ''
        numero = request.POST.get('numero', '') or ''
        bairro = request.POST.get('bairro', '') or ''
        cidade = request.POST.get('cidade', '') or ''
        estado = request.POST.get('estado', '') or ''

        # ----------------------------------------------------------------------
        # FOTOS
        # ----------------------------------------------------------------------

        foto_principal = request.FILES.get('foto_principal')
        fotos_galeria = request.FILES.getlist('fotos_galeria')

        # ----------------------------------------------------------------------
        # CONVERSÃO DO VALOR
        # ----------------------------------------------------------------------

        try:
            if valor_da_tela:
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
            else:
                valor_final = 0.00
        except (ValueError, TypeError):
            valor_final = 0.00

        # ----------------------------------------------------------------------
        # USUÁRIO RESPONSÁVEL
        # ----------------------------------------------------------------------

        responsavel_usuario = None

        if usuario_id:
            responsavel_usuario = Usuario.objects.filter(
                pk=usuario_id
            ).first()

        elif request.user.is_authenticated:
            responsavel_usuario = request.user

        # ======================================================================
        # MODO EDIÇÃO
        # ======================================================================

        if imovel:

            imovel.nome = f"{tipo} {logradouro}, {numero}".strip()
            imovel.referencia = referencia
            imovel.valor_original = valor_final
            imovel.status = status
            imovel.proprietario_documento = proprietario_doc
            imovel.descricao = descricao
            imovel.quartos = quartos_val

            if responsavel_usuario:
                imovel.user = responsavel_usuario

            if foto_principal:
                imovel.foto_principal = foto_principal

            imovel.save()

            # Atualiza/cria endereço
            endereco, _ = EnderecoImovel.objects.get_or_create(
                imovel=imovel
            )

            endereco.cep = cep
            endereco.logradouro = logradouro
            endereco.numero = numero
            endereco.bairro = bairro
            endereco.localidade = cidade
            endereco.sigla_federacao = estado

            endereco.save()

            messages.success(
                request,
                "Imóvel atualizado com sucesso!"
            )

        # ======================================================================
        # MODO CRIAÇÃO
        # ======================================================================

        else:

            nome_imovel = f"{tipo} {logradouro}, {numero}".strip()
            tipo_norm = tipo.lower()

            # SALA COMERCIAL
            if 'sala' in tipo_norm:
                novo_imovel = SalaComercial.objects.create(
                    nome=nome_imovel,
                    referencia=referencia,
                    valor_original=valor_final,
                    status=status,
                    proprietario_documento=proprietario_doc,
                    descricao=descricao,
                    user=responsavel_usuario,
                    foto_principal=foto_principal,
                    quartos=quartos_val,
                    area_util=50.0
                )

            # GALPÃO COMERCIAL
            elif 'galp' in tipo_norm:
                novo_imovel = GalpaoComercial.objects.create(
                    nome=nome_imovel,
                    referencia=referencia,
                    valor_original=valor_final,
                    status=status,
                    proprietario_documento=proprietario_doc,
                    descricao=descricao,
                    user=responsavel_usuario,
                    foto_principal=foto_principal,
                    quartos=quartos_val,
                    area_util=200.0
                )

            # APARTAMENTO
            elif 'apartamento' in tipo_norm or 'apto' in tipo_norm:
                area_util_val = request.POST.get('area_util') or 0.0
                num_suites_val = request.POST.get('numero_suites') or 0

                try:
                    area_util_val = float(area_util_val)
                except (ValueError, TypeError):
                    area_util_val = 0.0

                try:
                    num_suites_val = int(num_suites_val)
                except (ValueError, TypeError):
                    num_suites_val = 0

                novo_imovel = Apartamento.objects.create(
                    nome=nome_imovel,
                    referencia=referencia,
                    valor_original=valor_final,
                    status=status,
                    proprietario_documento=proprietario_doc,
                    descricao=descricao,
                    user=responsavel_usuario,
                    foto_principal=foto_principal,
                    quartos=quartos_val,
                    area_util=area_util_val,
                    numero_dormitorios=quartos_val,
                    numero_suites=num_suites_val
                )

            # TERRENO
            elif 'terreno' in tipo_norm:
                novo_imovel = Terreno.objects.create(
                    nome=nome_imovel,
                    referencia=referencia,
                    valor_original=valor_final,
                    status=status,
                    proprietario_documento=proprietario_doc,
                    descricao=descricao,
                    user=responsavel_usuario,
                    foto_principal=foto_principal,
                    quartos=quartos_val,
                    metragem=300.0
                )

            # SÍTIO
            elif 'sitio' in tipo_norm or 'sítio' in tipo_norm:
                novo_imovel = Sitio.objects.create(
                    nome=nome_imovel,
                    referencia=referencia,
                    valor_original=valor_final,
                    status=status,
                    proprietario_documento=proprietario_doc,
                    descricao=descricao,
                    user=responsavel_usuario,
                    foto_principal=foto_principal,
                    quartos=quartos_val,
                    area_total=1000.0,
                    benfeitorias=''
                )

            # CHÁCARA
            elif 'chacara' in tipo_norm or 'chácara' in tipo_norm:
                novo_imovel = Chacara.objects.create(
                    nome=nome_imovel,
                    referencia=referencia,
                    valor_original=valor_final,
                    status=status,
                    proprietario_documento=proprietario_doc,
                    descricao=descricao,
                    user=responsavel_usuario,
                    foto_principal=foto_principal,
                    quartos=quartos_val,
                    area_total=1000.0,
                    area_construida=100.0,
                    numero_casas=1
                )

            # CASA
            elif 'casa' in tipo_norm:
                area_terreno_val = request.POST.get('area_terreno') or 200.0
                area_construcao_val = request.POST.get('area_construcao') or 100.0
                num_suites_val = request.POST.get('numero_suites') or 0

                try:
                    area_terreno_val = float(area_terreno_val)
                except (ValueError, TypeError):
                    area_terreno_val = 200.0

                try:
                    area_construcao_val = float(area_construcao_val)
                except (ValueError, TypeError):
                    area_construcao_val = 100.0

                try:
                    num_suites_val = int(num_suites_val)
                except (ValueError, TypeError):
                    num_suites_val = 0

                novo_imovel = Casa.objects.create(
                    nome=nome_imovel,
                    referencia=referencia,
                    valor_original=valor_final,
                    status=status,
                    proprietario_documento=proprietario_doc,
                    descricao=descricao,
                    user=responsavel_usuario,
                    foto_principal=foto_principal,
                    quartos=quartos_val,
                    area_terreno=area_terreno_val,
                    area_construcao=area_construcao_val,
                    numero_dormitorios=quartos_val,
                    numero_suites=num_suites_val
                )

            # IMÓVEL GENÉRICO
            else:
                novo_imovel = Imovel.objects.create(
                    nome=nome_imovel,
                    referencia=referencia,
                    valor_original=valor_final,
                    status=status,
                    proprietario_documento=proprietario_doc,
                    descricao=descricao,
                    user=responsavel_usuario,
                    foto_principal=foto_principal,
                    quartos=quartos_val
                )

            # ENDEREÇO DO IMÓVEL
            EnderecoImovel.objects.create(
                cep=cep,
                logradouro=logradouro,
                numero=numero,
                bairro=bairro,
                localidade=cidade,
                sigla_federacao=estado,
                imovel=novo_imovel
            )

            # GALERIA DE FOTOS
            for foto in fotos_galeria:
                FotosImovel.objects.create(
                    imovel=novo_imovel,
                    caminho=foto
                )

            messages.success(
                request,
                "Imóvel cadastrado com sucesso!"
            )

        return redirect('buscar_imoveis')

    # GET
    todos_usuarios = Usuario.objects.all()

    return render(
        request,
        'cadastro_imoveis.html',
        {
            'imovel': imovel,
            'usuarios': todos_usuarios
        }
    )

def excluir_imovel_view(request, pk):
    """
    Remove um imóvel do catálogo.
    """
    imovel = get_object_or_404(
        Imovel,
        pk=pk
    )

    imovel.delete()

    messages.success(
        request,
        "Imóvel excluído com sucesso!"
    )

    return redirect('buscar_imoveis')

# ==============================================================================
# MÓDULO 3: GESTÃO DE CLIENTES
# ==============================================================================

def cadastro_proprietario_view(request):
    """
    Cadastro de vendedores/proprietários.
    """
    if request.method == "POST":
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        telefone_num = request.POST.get('telefone')
        senha = request.POST.get('senha') or '123456'

        # Limpeza do CPF para gerar o username automaticamente
        cpf_limpo = re.sub(r'\D', '', cpf) if cpf else ''
        username = cpf_limpo if cpf_limpo else f"prop_{PessoaFisica.objects.count() + 1}"

        if PessoaFisica.objects.filter(username=username).exists():
            messages.error(
                request,
                "Este CPF ou nome de usuário já está cadastrado."
            )
            return render(
                request,
                'cadastro_proprietario.html'
            )

        novo_vendedor = PessoaFisica(
            username=username,
            nome=nome,
            cpf=cpf,
            role='corretor'
        )
        novo_vendedor.set_password(senha)
        novo_vendedor.save()

        if telefone_num:
            Telefone.objects.create(
                usuario=novo_vendedor,
                telefone=telefone_num
            )

        messages.success(
            request,
            f"Vendedor/Proprietário {nome} cadastrado com sucesso!"
        )

        return redirect('home')

    return render(
        request,
        'cadastro_proprietario.html'
    )


def buscar_proprietario(request):
    """
    Pesquisa de proprietários cadastrados com base no nome ou CPF.
    """
    query = request.GET.get('q', '').strip()
    
    # Filtra por role de proprietário/corretor ou traz todos se preferir, 
    # ajustando conforme a lógica do seu modelo PessoaFisica.
    proprietarios = PessoaFisica.objects.filter(role='corretor').prefetch_related('telefones')

    if query:
        proprietarios = proprietarios.filter(
            Q(nome__icontains=query) | Q(cpf__icontains=query)
        )

    context = {
        'proprietarios': proprietarios,
    }
    return render(request, 'buscar_proprietario.html', context)


def cadastro_comprador_view(request, pk=None):
    """
    Cadastro e edição de compradores.
    """
    comprador = None
    telefone_str = ""

    if pk:
        comprador = get_object_or_404(
            PessoaFisica,
            pk=pk
        )

        primeiro_telefone = comprador.telefones.first()

        if primeiro_telefone:
            telefone_str = primeiro_telefone.telefone

    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        telefone = request.POST.get('telefone')
        faixa_busca = request.POST.get('faixa_busca')

        senha = (
            request.POST.get('senha')
            or '123456'
        )

        cpf_limpo = (
            re.sub(r'\D', '', cpf)
            if cpf
            else ''
        )

        telefone_num = (
            re.sub(r'\D', '', telefone)
            if telefone
            else None
        )

        # EDIÇÃO
        if comprador:
            comprador.nome = nome
            comprador.cpf = cpf
            comprador.save()

            if telefone_num:
                tel_obj, _ = Telefone.objects.get_or_create(
                    usuario=comprador
                )
                tel_obj.telefone = telefone_num
                tel_obj.save()

            messages.success(
                request,
                f"Comprador {nome} atualizado com sucesso!"
            )

        # CRIAÇÃO
        else:
            username = (
                cpf_limpo
                if cpf_limpo
                else f"comprador_{PessoaFisica.objects.count() + 1}"
            )

            # Validação para evitar duplicidade de CPF / Username
            if PessoaFisica.objects.filter(Q(username=username) | Q(cpf=cpf)).exists():
                messages.error(
                    request,
                    "Já existe um cadastro com este CPF."
                )
                return render(
                    request,
                    'cadastro_comprador.html',
                    {
                        'comprador': comprador,
                        'telefone_str': telefone_str
                    }
                )

            novo_comprador = PessoaFisica(
                username=username,
                nome=nome,
                cpf=cpf,
                role='comprador'
            )
            novo_comprador.set_password(senha)
            novo_comprador.save()

            if telefone_num:
                Telefone.objects.create(
                    usuario=novo_comprador,
                    telefone=telefone_num
                )

            messages.success(
                request,
                f"Comprador {nome} cadastrado com sucesso!"
            )

        return redirect('lista_compradores')

    return render(
        request,
        'cadastro_comprador.html',
        {
            'comprador': comprador,
            'telefone_str': telefone_str
        }
    )

def lista_compradores_view(request):
    """
    Lista todos os compradores cadastrados.
    """
    compradores = (
        PessoaFisica.objects
        .filter(role='comprador')
        .prefetch_related('telefones')
    )

    return render(
        request,
        'lista_compradores.html',
        {
            'compradores': compradores
        }
    )

def excluir_comprador_view(request, pk):
    """
    Exclui um comprador.
    """
    comprador = get_object_or_404(
        PessoaFisica,
        pk=pk
    )

    if request.method == 'POST':
        comprador.delete()

        messages.success(
            request,
            "Comprador excluído com sucesso!"
        )

        return redirect('lista_compradores')

    return redirect('lista_compradores')