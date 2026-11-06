"""
Testes da API (core). Por enquanto cobre só o endpoint /api/imoveis/,
criado para a busca de imóveis do siteapp consumir via JavaScript (fetch).

Rodar apenas esses testes:
    python manage.py test core
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Usuario, Imovel, PessoaFisica, Venda
from io import BytesIO
from PIL import Image
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile


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


# Tests
class PessoaFisicaTest(APITestCase):

    def setUp(self):
        self.image_data = BytesIO()
        self.image = Image.new('RGB', (100, 100), 'white')
        self.image.save(self.image_data, format='png')
        self.image_data.seek(0)

    def test_can_add_a_new_pessoa_fisica(self):

        payload = {
            "username": "username-teste",
            "nome": "pessoa-fisica1",
            "password": "123",
            "foto": SimpleUploadedFile("test.png", self.image_data.read(), content_type='image/png'),
            "role": "admin",
            "cpf": "902.878.858-10",
            "rg": "24.043.607-6"
        }

        response = self.client.post(reverse("pessoa-fisica"), payload)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertFalse("password" in response.json(), "Password should not be displayed.")

        created_pessoa_fisica = PessoaFisica.objects.get(nome=payload["nome"])

        campos_simples = ["username", "nome", "role", "cpf", "rg"]
        for campo in campos_simples:
            with self.subTest(campo=campo):
                self.assertEqual(payload[campo], response.data[campo])
                self.assertEqual(payload[campo], getattr(created_pessoa_fisica, campo))

        self.assertTrue(created_pessoa_fisica.check_password(payload["password"]))
        
        self.assertTrue(created_pessoa_fisica.foto)
        self.assertIn("test", created_pessoa_fisica.foto.name)
        self.assertIn("test", response.data["foto"])


class VendaTest(APITestCase):

    def setUp(self):
        self.vendedor = Usuario.objects.create_user(
            username="vendedor-teste",
            password="123",
        )
        self.comprador = Usuario.objects.create_user(
            username="comprador-teste",
            password="123",
        )

        self.imovel = Imovel.objects.create(
            nome="imovel-teste",
            quartos=2,
            user=self.vendedor,
            valor_original=250000.00,
        )
    
    def test_can_add_a_new_venda(self):

        payload = {
            "imovel": self.imovel.id,
            "comprador": self.comprador.id,
            "vendedor": self.vendedor.id,
            "preco_pedido": "350000.00",
            "preco_final": "340000.00",
            "data_fechamento": "2026-12-01",
            "observacoes": "venda-teste",
            "status": "executando",
        }

        response = self.client.post(reverse("venda-list"), payload)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.content)

        created_venda = Venda.objects.get(id=response.data["id"])

        campos_simples = [
            "preco_pedido", "preco_final", "data_fechamento", "observacoes", "status"
        ]
        for campo in campos_simples:
            with self.subTest(campo=campo):
                self.assertEqual(payload[campo], response.data[campo])
                self.assertEqual(payload[campo], str(getattr(created_venda, campo)))

        for campo in ["imovel", "comprador", "vendedor"]:
            with self.subTest(campo=campo):
                self.assertEqual(payload[campo], response.data[campo])
                self.assertEqual(payload[campo], getattr(created_venda, f"{campo}_id"))

        self.assertEqual(created_venda.data_publicacao, date.today())


class ImovelTest(APITestCase):

    def setUp(self):
        self.image_data = BytesIO()
        self.image = Image.new('RGB', (100, 100), 'white')
        self.image.save(self.image_data, format='png')
        self.image_data.seek(0)

        self.usuario = Usuario.objects.create_user(
            username="usuario-imovel-teste", password="123"
        )
        self.client.force_authenticate(user=self.usuario)

    def test_can_add_a_new_imovel(self):

        endereco = {
            "bairro": "Centro",
            "logradouro": "Rua Teste",
            "numero": "123",
            "complemento": "Apto 4",
            "cep": "13930-000",
            "localidade": "Serra Negra",
            "sigla_federacao": "SP",
        }

        payload = {
            "nome": "imovel1",
            "referencia": "REF-001",
            "quartos": 3,
            "descricao": "imovel-teste",
            "foto_principal": SimpleUploadedFile("test.png", self.image_data.read(), content_type='image/png'),
            "user": self.usuario.id,
            "proprietario_documento": "902.878.858-10",
            "valor_original": 450000.5,
            "status": "disponivel",
        }

        # Multipart não aceita dict aninhado: usa-se a notação "endereco.campo"
        for campo, valor in endereco.items():
            payload[f"endereco.{campo}"] = valor

        response = self.client.post(reverse("imovel-admin-list"), payload)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.content)

        created_imovel = Imovel.objects.get(nome=payload["nome"])

        campos_simples = [
            "nome", "referencia", "quartos", "descricao",
            "proprietario_documento", "valor_original", "status",
        ]
        for campo in campos_simples:
            with self.subTest(campo=campo):
                self.assertEqual(payload[campo], response.data[campo])
                self.assertEqual(payload[campo], getattr(created_imovel, campo))

        # Foreign key
        self.assertEqual(payload["user"], response.data["user"])
        self.assertEqual(payload["user"], created_imovel.user_id)

        # Endereço (OneToOne, aninhado)
        created_endereco = created_imovel.endereco
        for campo, valor in endereco.items():
            with self.subTest(endereco=campo):
                self.assertEqual(valor, response.data["endereco"][campo])
                self.assertEqual(valor, getattr(created_endereco, campo))

        # Foto
        self.assertTrue(created_imovel.foto_principal)
        self.assertIn("test", created_imovel.foto_principal.name)
        self.assertIn("test", response.data["foto_principal"])
