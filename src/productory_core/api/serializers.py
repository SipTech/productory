from __future__ import annotations

from datetime import date

from rest_framework import serializers


class DashboardKPIQuerySerializer(serializers.Serializer):
    store = serializers.SlugField(required=False, default="default")
    date_from = serializers.DateField(required=False, source="from")
    date_to = serializers.DateField(required=False, source="to")
    low_stock_threshold = serializers.IntegerField(required=False, default=5, min_value=0)

    def validate(self, attrs):
        date_from: date | None = attrs.get("from")
        date_to: date | None = attrs.get("to")
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError({"from": "`from` must be <= `to`."})
        return attrs
