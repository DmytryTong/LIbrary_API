from django.urls import path

from payment.views import (
    PaymentDetailView,
    PaymentListView,
    PaymentCreateView,
    create_payment_session,
)

urlpatterns = [
    path("", PaymentListView.as_view(), name="payment-list"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("success/<int:pk>/", create_payment_session, name="success"),
    path("cancel/", create_payment_session, name="cancel"),
]

app_name = "payments"
