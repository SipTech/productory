from django.urls import path

from productory_core.api.views import DashboardKPIView

urlpatterns = [
    path("dashboard/kpis/", DashboardKPIView.as_view(), name="productory-dashboard-kpis"),
]
