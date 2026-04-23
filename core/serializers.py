from rest_framework import serializers
from .models import *

# usuarios com role CUSTOMER. Depois vou fazer o especifico
# p/ admin
class PessoaFisicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PessoaFisica
        fields = ['username', 'nome', 'password', 'email', 'role', 'foto', 'cpf', 'rg']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = PessoaFisica.objects.create_user(**validated_data)
        return user