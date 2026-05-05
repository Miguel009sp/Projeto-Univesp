from rest_framework import serializers
from .models import *

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = fields = ['username', 'nome', 'password', 'email', 'role', 'foto']
        extra_kwargs = {'password': {'write_only': True}}
    
# usuarios com role CUSTOMER. Depois vou fazer o especifico
# p/ admin
class PessoaFisicaSerializer(UsuarioSerializer):
    class Meta(UsuarioSerializer.Meta):
        model = PessoaFisica
        fields = UsuarioSerializer.Meta.fields + ['cpf', 'rg']

    def create(self, validated_data):
        user = PessoaFisica.objects.create_user(**validated_data)
        return user
    
class PessoaJuridicaSerializer(UsuarioSerializer):
    class Meta(UsuarioSerializer.Meta): 
        model = PessoaJuridica
        fields = UsuarioSerializer.Meta.fields + ['cnpj', 'nome_empresa', 'nome_comercial']

    def create(self, validated_data):
        user = PessoaJuridica.objects.create_user(**validated_data)
        return user
    
class TelefoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telefone
        fields = '__all__'

class EnderecoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnderecoUsuario
        fields = '__all__'
    

# Imoveis
class ImovelSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Imovel
        fields = '__all__'

class FotosImovelSerializer(serializers.ModelSerializer):
    class Meta: 
        model = FotosImovel
        fields = '__all__'

class TerrenoSerializer(ImovelSerializer):
    class Meta(ImovelSerializer.Meta):
        model = Terreno
        fields = ImovelSerializer.Meta.fields + '__all__'

        