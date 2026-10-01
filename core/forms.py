from django import forms
from django.core.exceptions import ValidationError
from .models import (
    EnderecoImovel, FotosImovel, Terreno, Casa, 
    Apartamento, DetalhesApartamento, SalaComercial, 
    GalpaoComercial, Sitio, Chacara
)

# --- CAMPOS COMPARTILHADOS (HERDADOS DE IMOVEL) ---
CAMPOS_BASE_IMOVEL = [
    'nome', 
    'referencia', 
    'descricao', 
    'foto_principal', 
    'proprietario_documento', 
    'valor_original', 
    'status'
]

# Widgets padrão para padronizar o design dos inputs e adicionar máscaras/placeholders
WIDGETS_BASE = {
    'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Casa de Praia com Piscina'}),
    'referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: REF1020'}),
    'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva os detalhes do imóvel...'}),
    'foto_principal': forms.FileInput(attrs={'class': 'form-control'}),
    'proprietario_documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF ou CNPJ (somente números)'}),
    'valor_original': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'R$ 0,00', 'step': '0.01'}),
    'status': forms.Select(attrs={'class': 'form-select'}),
}


# --- MIXIN DE VALIDAÇÃO COMPARTILHADA ---
class BaseImovelFormMixin:
    """Validações personalizadas aplicadas a todos os tipos de imóveis."""
    
    def clean_valor_original(self):
        valor = self.cleaned_data.get('valor_original')
        if valor is not None and valor <= 0:
            raise ValidationError("O valor do imóvel deve ser maior que zero.")
        return valor

    def clean_proprietario_documento(self):
        doc = self.cleaned_data.get('proprietario_documento', '')
        # Remove caracteres não numéricos para padronizar no banco
        doc_limpo = ''.join(filter(str.isdigit, doc))
        if doc_limpo and len(doc_limpo) not in [11, 14]:
            raise ValidationError("Informe um CPF (11 dígitos) ou CNPJ (14 dígitos) válido.")
        return doc_limpo


# --- FORMULÁRIO DE ENDEREÇO (COM SUPORTE A BUSCA DE CEP AUTOMÁTICA) ---
class EnderecoImovelForm(forms.ModelForm):
    class Meta:
        model = EnderecoImovel
        fields = ['cep', 'logradouro', 'numero', 'bairro', 'complemento', 'localidade', 'sigla_federacao']
        widgets = {
            'cep': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '00000-000',
                'id': 'id_cep',
                'onkeyup': 'buscarCEP(this.value)'  # Gatilho JS para busca automática
            }),
            'logradouro': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_logradouro'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nº'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_bairro'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apto, Bloco, etc.'}),
            'localidade': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_localidade'}),
            'sigla_federacao': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_uf', 'maxlength': '2'}),
        }


# --- FORMULÁRIO DE FOTOS (GALERIA MULTIPLE UPLOAD) ---
class FotosImovelForm(forms.ModelForm):
    class Meta:
        model = FotosImovel
        fields = ['caminho']
        widgets = {
            'caminho': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        }


# --- FORMULÁRIOS ESPECÍFICOS POR TIPO DE IMÓVEL ---

class TerrenoForm(BaseImovelFormMixin, forms.ModelForm):
    class Meta:
        model = Terreno
        fields = CAMPOS_BASE_IMOVEL + ['metragem']
        widgets = {**WIDGETS_BASE, 'metragem': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm²'})}


class CasaForm(BaseImovelFormMixin, forms.ModelForm):
    class Meta:
        model = Casa
        fields = CAMPOS_BASE_IMOVEL + ['area_terreno', 'area_construcao', 'numero_dormitorios', 'numero_suites']
        widgets = {
            **WIDGETS_BASE,
            'area_terreno': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm²'}),
            'area_construcao': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm²'}),
            'numero_dormitorios': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'numero_suites': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class ApartamentoForm(BaseImovelFormMixin, forms.ModelForm):
    class Meta:
        model = Apartamento
        fields = CAMPOS_BASE_IMOVEL + ['area_util', 'numero_dormitorios', 'numero_suites']
        widgets = {
            **WIDGETS_BASE,
            'area_util': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm²'}),
            'numero_dormitorios': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'numero_suites': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class DetalhesApartamentoForm(BaseImovelFormMixin, forms.ModelForm):
    class Meta:
        model = DetalhesApartamento
        fields = CAMPOS_BASE_IMOVEL + ['area_util', 'numero_dormitorios', 'numero_suites', 'bloco', 'andar']
        widgets = {
            **WIDGETS_BASE,
            'area_util': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm²'}),
            'numero_dormitorios': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'numero_suites': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'bloco': forms.TextInput(attrs={'class': 'form-control'}),
            'andar': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class SalaComercialForm(BaseImovelFormMixin, forms.ModelForm):
    class Meta:
        model = SalaComercial
        fields = CAMPOS_BASE_IMOVEL + ['area_util']
        widgets = {**WIDGETS_BASE, 'area_util': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm²'})}


class GalpaoComercialForm(BaseImovelFormMixin, forms.ModelForm):
    class Meta:
        model = GalpaoComercial
        fields = CAMPOS_BASE_IMOVEL + ['area_util']
        widgets = {**WIDGETS_BASE, 'area_util': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm²'})}


class SitioForm(BaseImovelFormMixin, forms.ModelForm):
    class Meta:
        model = Sitio
        fields = CAMPOS_BASE_IMOVEL + ['area_total', 'benfeitorias']
        widgets = {
            **WIDGETS_BASE,
            'area_total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm² ou ha'}),
            'benfeitorias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ChacaraForm(BaseImovelFormMixin, forms.ModelForm):
    class Meta:
        model = Chacara
        fields = CAMPOS_BASE_IMOVEL + ['area_total', 'area_construida', 'numero_casas']
        widgets = {
            **WIDGETS_BASE,
            'area_total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm²'}),
            'area_construida': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm²'}),
            'numero_casas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        