from rest_framework import serializers
from .models import *

class PessoaFisicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PessoaFisica
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = PessoaFisica.objects.create_user(**validated_data)
        return user