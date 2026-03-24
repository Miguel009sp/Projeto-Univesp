from django.shortcuts import render

def home(request):
    # O 'render' é quem vai buscar o seu arquivo index.html na pasta templates
    return render(request, 'index.html')