from __future__ import annotations

from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from productory_core.api.serializers import DashboardKPIQuerySerializer
from productory_core.services.dashboard_kpis import get_store_kpis


class DashboardKPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        query = DashboardKPIQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        try:
            payload = get_store_kpis(
                store_slug=query.validated_data["store"],
                date_from=query.validated_data.get("from"),
                date_to=query.validated_data.get("to"),
                low_stock_threshold=query.validated_data["low_stock_threshold"],
            )
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)}) from exc
        return Response(payload)
