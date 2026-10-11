import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto.settings')

# Inicializa o aplicativo WSGI do Django primeiro
application = get_wsgi_application()

# Executa as migrações e garante que as tabelas existam logo na subida do servidor
from django.core.management import call_command
try:
    call_command('migrate', interactive=False)
    print("Migrações executadas com sucesso no arranque!")
except Exception as e:
    print(f"Erro ao rodar migrações: {e}")
    