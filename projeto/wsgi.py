import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto.settings')

# Força a execução das migrações automaticamente ao iniciar no Render
try:
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Erro ao rodar migrações automaticamente: {e}")

application = get_wsgi_application()
