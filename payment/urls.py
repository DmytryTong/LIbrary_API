from django.urls import path

from payment.views import PaymentDetailView, PaymentListView


urlpatterns = [
    path("", PaymentListView.as_view(), name="payment-list"),
    path(
        "<int:pk>/",
        PaymentDetailView.as_view(),
        name="payment-detail"
    ),
]

app_name = "payments"
