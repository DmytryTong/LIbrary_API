from django.urls import path

from payment.views import (
    PaymentDetailView,
    PaymentListView,
    cancel_payment,
    success_payment,
)

urlpatterns = [
    path("", PaymentListView.as_view(), name="payment-list"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("success/", success_payment, name="success-payment"),
    path("cancel/", cancel_payment, name="cancel-payment"),
]

app_name = "payments"
