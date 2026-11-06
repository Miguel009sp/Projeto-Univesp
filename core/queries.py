from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

from .models import Venda

def vendas_por_mes():
    return (
        Venda.objects
        .filter(status="finalizada", data_fechamento__isnull=False)
        .annotate(mes=TruncMonth("data_fechamento"))
        .values("mes")                                   # <- transforma em dicts e define o GROUP BY
        .annotate(total=Sum("preco_final"), quantidade=Count("id"))
        .order_by("mes")
    )

def vendas_por_status():
    return(
        Venda.objects
        .values("status")
        .annotate(quantidade=Count("id"))
        .order_by("status")
    )