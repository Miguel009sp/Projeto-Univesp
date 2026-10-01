from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static 
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Importa as views do módulo core de forma limpa e explícita
from .views import (
    TerrenoViewSet, CasaViewSet, SalaComercialViewSet, GalpaoComercialViewSet,
    SitioViewSet, ChacaraViewSet, ApartamentoViewSet, VendaViewSet, FotosImovelViewSet,
    ImovelPublicoViewSet,
    ListCreatePessoaFisica, ListCreatePessoaJuridica, ListAllUsers, ListCreateTelefone,
    ListCreateEnderecoUsuario
)

# Configuração do Router para os ViewSets de Imóveis da API
router = DefaultRouter()
router.register(r'terrenos', viewset=TerrenoViewSet, basename='terreno')
router.register(r'casas', viewset=CasaViewSet, basename='casa')
router.register(r'salas-comerciais', viewset=SalaComercialViewSet, basename='salacomercial')
router.register(r'galpoes-comerciais', viewset=GalpaoComercialViewSet, basename='galpaocomercial')
router.register(r'sitios', viewset=SitioViewSet, basename='sitio')
router.register(r'chacaras', viewset=ChacaraViewSet, basename='chacara')
router.register(r'apartamentos', viewset=ApartamentoViewSet, basename='apartamento')
router.register(r'imoveis', viewset=ImovelPublicoViewSet, basename='imovel')
router.register(r'vendas', viewset=VendaViewSet)
router.register(r'fotos-imovel', viewset=FotosImovelViewSet)

urlpatterns = [   
    # --- ROTAS DA API (Sincronizadas com o prefixo 'api/' do projeto principal) ---
    path('', include(router.urls)),

    # Endpoints de Autenticação JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Endpoints de Usuários e Cadastros
    path('pessoa-fisica/', ListCreatePessoaFisica.as_view()),
    path('pessoa-juridica/', ListCreatePessoaJuridica.as_view()),
    path('usuarios/', ListAllUsers.as_view()),
    path('telefones/', ListCreateTelefone.as_view()),
    path('enderecos-usuario/', ListCreateEnderecoUsuario.as_view()),
]

# Configuração para exibir as fotos dos imóveis no navegador
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
