import os
from pathlib import Path
from datetime import timedelta
import dj_database_url

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# CHAVE DE SEGURANÇA (Mantenha em segredo em produção)
SECRET_KEY = 'django-insecure-+n6%z^*ktabi$6_tjhu%)jgqjgcye-61mozdc^*+c^bn2w+7l#'

# DEBUG ativado para desenvolvimento
DEBUG = True

ALLOWED_HOSTS = ['.vercel.app', '127.0.0.1', 'localhost']

# Definição das Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'siteapp',
    'rest_framework',
    'core',
    'rest_framework_simplejwt',
    'corsheaders',
]

# Modelo de usuário personalizado
AUTH_USER_MODEL = 'core.Usuario'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Middleware de CORS deve vir antes do Common
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Permite que o seu Front-end (JavaScript) acesse a API sem bloqueios
CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'projeto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # O Django buscará pastas 'templates' dentro de cada APP
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media', # Necessário para fotos
            ],
        },
    },
]

WSGI_APPLICATION = 'projeto.wsgi.application'

# --- CONFIGURAÇÃO DE BANCO DE DADOS ---
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}

# --- CONFIGURAÇÃO DE SESSÕES AJUSTADA PARA VELOCIDADE LOCAL ---
# Conecta as sessões diretamente ao banco padrão SQLite.
# Isso evita o travamento de comunicação entre múltiplos processos do VS Code (Threads).
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Armazenamento das mensagens via cookies estável para o ambiente de testes
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'


# Validação de senhas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Configurações do REST Framework (Ajustado para aceitar formulário tradicional e JWT)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',  # Destrava o login tradicional HTML
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Mantém a API funcionando para o Front
    )
}

# Configuração do Token JWT
SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1)
}

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos Estáticos (CSS, JS)
STATIC_URL = 'static/'

# Mantido vazio para evitar redundância. O Django busca automaticamente as pastas
# "static" que estiverem dentro das aplicações ('siteapp' e 'core') por causa do APP_DIRS=True.
STATICFILES_DIRS = []

# Configurações de Mídia (Fotos dos Imóveis)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Tipo padrão de ID
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
import os
from pathlib import Path

# Caso já não tenha o BASE_DIR definido no topo do arquivo
BASE_DIR = Path(__file__).resolve().parent.parent

# URL que o navegador vai usar para acessar as mídias (ex: /media/imagem.jpg)
MEDIA_URL = '/media/'

# Caminho físico no seu computador onde os arquivos serão salvos
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')