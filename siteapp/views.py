from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages

def logout_view(request):
    logout(request)
    return redirect('login') # Redireciona para a página de login após o logout


def login_view(request):
    if request.method == "POST":
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
  # LOGIN FIXO verificação (você pode mudar depois)
        
        if usuario == 'bragatto' and senha == '123456':
            return redirect('home')  # Redireciona para a página home
        else:
            return render(request, 'login.html', {
                'erro': 'Usuário ou senha inválidos'
            })

    return render(request, 'login.html')

def home_view(request):
    return render(request, 'home.html') 


def buscar_imoveis_view(request):
    return render(request, 'buscar_imoveis.html')

def cadastro_proprietario_view(request):
    return render(request, 'cadastro_proprietario.html')    

def cadastro_imoveis_view(request):
    return render(request, 'cadastro_imoveis.html')

def cadastro_comprador_view(request):
    return render(request, 'cadastro_comprador.html')



