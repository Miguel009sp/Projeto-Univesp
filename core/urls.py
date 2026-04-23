from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [   

    # pessoa fisica url (GET e POST)
    path('pessoa_fisica', ListCreatePessoaFisica.as_view())
]