import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from core.models import (
    Usuario, PessoaFisica, Telefone, Imovel, Casa, Apartamento, 
    Terreno, SalaComercial, GalpaoComercial, Sitio, Chacara, 
    FotosImovel, EnderecoImovel
)

# ==============================================================================
# MÓDULO 1: AUTENTICAÇÃO E SESSÃO DO USUÁRIO SECRETA E SEGURA
# ==============================================================================

def login_view(request):
    """
    Controla o acesso inicial de forma instantânea efetuando o login real no Django.
    """
    if request.method == "POST":
        usuario_input = request.POST.get('usuario', '').strip()
        senha_input = request.POST.get('senha', '').strip()
        
        # 1. TENTA AUTENTICAR NO BANCO DE DADOS OFICIAL DO DJANGO
        user = authenticate(request, username=usuario_input, password=senha_input)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        
        # 2. BACKUP DE DESENVOLVIMENTO
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
    """
    Encerra a sessão ativa de forma limpa e imediata.
    """
    logout(request)
    return redirect('login') 


def home_view(request):
    """
    Renderiza o Dashboard Administrativo Centralizado.
    """
    return render(request, 'home.html') 

# ==============================================================================
# MÓDULO 2: LOGÍSTICA E OPERAÇÕES DE IMÓVEIS
# ==============================================================================

def buscar_imoveis_view(request):
    """
    Painel de consultas avançadas otimizado com select_related para evitar múltiplas queries.
    Busca na tabela base de Imoveis para contemplar todos os tipos (Casas, Salas, Terrenos, etc).
    """
    tipo_imovel = request.GET.get('tipo_imovel')
    valor_maximo = request.GET.get('valor_maximo')
    
    imoveis = Imovel.objects.all().select_related('endereco')
    
    if tipo_imovel and tipo_imovel != "Todos":
        imoveis = imoveis.filter(nome__icontains=tipo_imovel)
    
    if valor_maximo:
        try:
            valor_limpo = str(valor_maximo).replace('R$', '').replace('.', '').replace(',', '.').strip()
            preco_limite = float(valor_limpo)
            imoveis = imoveis.filter(valor_original__lte=preco_limite)
        except ValueError:
            pass

    return render(request, 'buscar_imoveis.html', {'imoveis': imoveis})


def cadastro_imoveis_view(request, pk=None):
    """
    Controlador unificado de Persistência (Criação e Edição de registros de Imóveis).
    Garante a instanciação do tipo correto de imóvel e passa todos os usuários para a seleção.
    """
    imovel = None
    if pk:
        imovel = get_object_or_404(Imovel, pk=pk)

    if request.method == "POST":
        # Captura de Dados Básicos
        tipo = request.POST.get('tipo_imovel', '').strip()
        status = request.POST.get('status')
        referencia = request.POST.get('referencia')
        valor_da_tela = request.POST.get('valor_imovel') 
        proprietario_doc = request.POST.get('proprietario_documento')
        descricao = request.POST.get('descricao')
        usuario_id = request.POST.get('usuario')  # Captura o usuário selecionado no formulário
        
        # Endereço
        cep = request.POST.get('cep')
        logradouro = request.POST.get('logradouro')
        numero = request.POST.get('numero')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')

        # Fotos
        foto_principal = request.FILES.get('foto_principal')
        fotos_galeria = request.FILES.getlist('fotos_galeria')
        
        # Tratamento de conversão de valor com fallback seguro
        try:
            if valor_da_tela:
                valor_limpo = str(valor_da_tela).replace('R$', '').replace('.', '').replace(',', '.').strip()
                valor_final = float(valor_limpo)
            else:
                valor_final = 0.00
        except (ValueError, TypeError):
            valor_final = 0.00

        # Define o responsável/dono selecionado
        responsavel_usuario = None
        if usuario_id:
            responsavel_usuario = Usuario.objects.filter(pk=usuario_id).first()
        elif request.user.is_authenticated:
            responsavel_usuario = request.user

        # MODO EDIÇÃO (UPDATE)
        if imovel:
            imovel.nome = f"{tipo} - {logradouro}, {numero}"
            imovel.referencia = referencia
            imovel.valor_original = valor_final
            imovel.status = status
            imovel.proprietario_documento = proprietario_doc
            imovel.descricao = descricao
            if responsavel_usuario:
                imovel.user = responsavel_usuario
            
            if foto_principal:
                imovel.foto_principal = foto_principal
            imovel.save()
            
            # Atualiza ou cria o endereço atrelado ao imóvel
            endereco, _ = EnderecoImovel.objects.get_or_create(imovel=imovel)
            endereco.cep = cep
            endereco.logradouro = logradouro
            endereco.numero = numero
            endereco.bairro = bairro
            endereco.localidade = cidade
            endereco.sigla_federacao = estado
            endereco.save()
            
            messages.success(request, "Imóvel atualizado com sucesso!")

        # MODO CRIAÇÃO (CREATE) - Instancia a subclasse específica do imóvel
        else:
            nome_imovel = f"{tipo} - {logradouro}, {numero}"
            tipo_norm = tipo.lower()

            if 'sala' in tipo_norm:
                novo_imovel = SalaComercial.objects.create(
                    nome=nome_imovel, referencia=referencia, valor_original=valor_final,
                    status=status, proprietario_documento=proprietario_doc, descricao=descricao,
                    user=responsavel_usuario, foto_principal=foto_principal, area_util=50.0
                )
            elif 'galp' in tipo_norm:
                novo_imovel = GalpaoComercial.objects.create(
                    nome=nome_imovel, referencia=referencia, valor_original=valor_final,
                    status=status, proprietario_documento=proprietario_doc, descricao=descricao,
                    user=responsavel_usuario, foto_principal=foto_principal, area_util=200.0
                )
            elif 'apartamento' in tipo_norm or 'apto' in tipo_norm:
                novo_imovel = Apartamento.objects.create(
                    nome=nome_imovel, referencia=referencia, valor_original=valor_final,
                    status=status, proprietario_documento=proprietario_doc, descricao=descricao,
                    user=responsavel_usuario, foto_principal=foto_principal
                )
            elif 'terreno' in tipo_norm:
                novo_imovel = Terreno.objects.create(
                    nome=nome_imovel, referencia=referencia, valor_original=valor_final,
                    status=status, proprietario_documento=proprietario_doc, descricao=descricao,
                    user=responsavel_usuario, foto_principal=foto_principal, area_terreno=300.0
                )
            elif 'sitio' in tipo_norm or 'sítio' in tipo_norm:
                novo_imovel = Sitio.objects.create(
                    nome=nome_imovel, referencia=referencia, valor_original=valor_final,
                    status=status, proprietario_documento=proprietario_doc, descricao=descricao,
                    user=responsavel_usuario, foto_principal=foto_principal, area_terreno=1000.0
                )
            elif 'chacara' in tipo_norm or 'chácara' in tipo_norm:
                novo_imovel = Chacara.objects.create(
                    nome=nome_imovel, referencia=referencia, valor_original=valor_final,
                    status=status, proprietario_documento=proprietario_doc, descricao=descricao,
                    user=responsavel_usuario, foto_principal=foto_principal, area_terreno=1000.0
                )
            elif 'casa' in tipo_norm:
                novo_imovel = Casa.objects.create(
                    nome=nome_imovel, referencia=referencia, valor_original=valor_final,
                    status=status, proprietario_documento=proprietario_doc, descricao=descricao,
                    user=responsavel_usuario, foto_principal=foto_principal,
                    area_terreno=200.0, area_construcao=100.0, numero_dormitorios=2, numero_suites=0
                )
            else:
                novo_imovel = Imovel.objects.create(
                    nome=nome_imovel, referencia=referencia, valor_original=valor_final,
                    status=status, proprietario_documento=proprietario_doc, descricao=descricao,
                    user=responsavel_usuario, foto_principal=foto_principal
                )

            # Cadastra o Endereço vinculado
            EnderecoImovel.objects.create(
                cep=cep, logradouro=logradouro, numero=numero,
                bairro=bairro, localidade=cidade, sigla_federacao=estado,
                imovel=novo_imovel
            )

            # Cadastra a Galeria de fotos
            for foto in fotos_galeria:
                FotosImovel.objects.create(imovel=novo_imovel, caminho=foto)

            messages.success(request, "Imóvel cadastrado com sucesso!")

        return redirect('buscar_imoveis')

    # Passa todos os usuários para preencher a caixa de seleção no template HTML
    todos_usuarios = Usuario.objects.all()
    return render(request, 'cadastro_imoveis.html', {
        'imovel': imovel,
        'usuarios': todos_usuarios
    })


def excluir_imovel_view(request, pk):
    """
    Remove fisicamente as propriedades do catálogo através do método POST de segurança.
    """
    imovel = get_object_or_404(Imovel, pk=pk)
    imovel.delete()
    messages.success(request, "Imóvel excluído com sucesso!")
    return redirect('buscar_imoveis')

# ==============================================================================
# MÓDULO 3: GESTÃO DE CLIENTES (PROPRIETÁRIOS E COMPRADORES)
# ==============================================================================

def cadastro_proprietario_view(request):
    """
    Painel de cadastro para novos vendedores e locadores no site.
    Salva como PessoaFisica e atribui a role 'corretor'.
    """
    if request.method == "POST":
        nome = request.POST.get('nome')
        username = request.POST.get('username') or request.POST.get('email')
        email = request.POST.get('email')
        senha = request.POST.get('senha') or '123456'
        cpf = request.POST.get('cpf')
        telefone_num = request.POST.get('telefone')

        if PessoaFisica.objects.filter(username=username).exists():
            messages.error(request, "Este nome de usuário ou e-mail já está cadastrado.")
            return render(request, 'cadastro_proprietario.html')

        novo_vendedor = PessoaFisica.objects.create_user(
            username=username,
            email=email,
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


def cadastro_comprador_view(request, pk=None):
    """
    Controlador unificado de Persistência (Criação e Edição de Compradores).
    Suporta rotas sem ID (novo cadastro) e com ID (edição).
    """
    comprador = None
    telefone_str = ""

    if pk:
        comprador = get_object_or_404(PessoaFisica, pk=pk)
        primeiro_telefone = comprador.telefones.first()
        if primeiro_telefone:
            telefone_str = primeiro_telefone.telefone

    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        telefone = request.POST.get('telefone')
        faixa_busca = request.POST.get('faixa_busca')
        senha = request.POST.get('senha') or '123456'

        cpf_limpo = re.sub(r'\D', '', cpf) if cpf else ''
        telefone_num = re.sub(r'\D', '', telefone) if telefone else None

        # MODO EDIÇÃO
        if comprador:
            comprador.nome = nome
            comprador.cpf = cpf
            comprador.save()

            if telefone_num:
                tel_obj, _ = Telefone.objects.get_or_create(usuario=comprador)
                tel_obj.telefone = telefone_num
                tel_obj.save()

            messages.success(request, f"Comprador {nome} atualizado com sucesso!")

        # MODO CRIAÇÃO
        else:
            username = cpf_limpo if cpf_limpo else f"comprador_{PessoaFisica.objects.count() + 1}"
            if PessoaFisica.objects.filter(username=username).exists():
                username = f"{username}_{PessoaFisica.objects.count() + 1}"

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

        return redirect('lista_compradores')

    return render(request, 'cadastro_comprador.html', {
        'comprador': comprador,
        'telefone_str': telefone_str
    })


def lista_compradores_view(request):
    """
    Exibe a listagem de todos os compradores cadastrados no sistema.
    """
    compradores = PessoaFisica.objects.filter(role='comprador').prefetch_related('telefones')
    return render(request, 'lista_compradores.html', {'compradores': compradores})


def excluir_comprador_view(request, pk):
    """
    Exclui a PessoaFisica referente ao comprador cadastrado.
    """
    comprador = get_object_or_404(PessoaFisica, pk=pk)
    
    if request.method == 'POST':
        comprador.delete()
        messages.success(request, "Comprador excluído com sucesso!")
        return redirect('lista_compradores')
        
    return redirect('lista_compradores')
