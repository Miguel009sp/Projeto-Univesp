"""
Testes da API (core). Por enquanto cobre só o endpoint /api/imoveis/,
criado para a busca de imóveis do siteapp consumir via JavaScript (fetch).

Rodar apenas esses testes:
    python manage.py test core
"""
from django.test import TestCase
from django.urls import reverse

from .models import Usuario, Imovel


class ImovelPublicoViewSetTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(username="dono_teste", password="x")
        Imovel.objects.create(nome="Casa - Rua A, 10", valor_original=200000, user=self.usuario)
        Imovel.objects.create(nome="Apartamento - Rua B, 20", valor_original=350000, user=self.usuario)
        Imovel.objects.create(nome="Casa - Rua C, 30", valor_original=500000, user=self.usuario)
        self.url = reverse('imovel-list')

    def _imoveis(self, resposta):
        # A view não usa paginação por padrão, mas isso pode mudar no futuro.
        dados = resposta.json()
        return dados if isinstance(dados, list) else dados.get('results', [])

    def test_lista_todos_os_imoveis(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(self._imoveis(resposta)), 3)

    def test_filtra_por_tipo_imovel(self):
        resposta = self.client.get(self.url, {'tipo_imovel': 'Casa'})
        imoveis = self._imoveis(resposta)
        self.assertEqual(len(imoveis), 2)
        self.assertTrue(all('Casa' in imovel['nome'] for imovel in imoveis))

    def test_filtra_por_valor_maximo(self):
        resposta = self.client.get(self.url, {'valor_maximo': '250000'})
        imoveis = self._imoveis(resposta)
        self.assertEqual(len(imoveis), 1)
        self.assertEqual(imoveis[0]['valor_original'], 200000)

    def test_resposta_inclui_endereco_aninhado(self):
        # O JS da busca depende de "endereco.logradouro" etc. existirem na resposta.
        resposta = self.client.get(self.url)
        imovel = self._imoveis(resposta)[0]
        self.assertIn('endereco', imovel)
