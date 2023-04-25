import stripe
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal

import borrowing
from borrowing.models import Borrowing
from config import settings
from payment.models import Payment
from payment.permissions import IsOwnerOrAdmin
from payment.serializers import PaymentSerializer


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.select_related("borrowing__user")
    serializer_class = PaymentSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            return queryset.filter(borrowing__user=self.request.user)
        return queryset.all()


class PaymentDetailView(generics.RetrieveDestroyAPIView):
    queryset = Payment.objects.select_related("borrowing__user")
    serializer_class = PaymentSerializer
    permission_classes = [
        IsOwnerOrAdmin,
    ]


class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.select_related("borrowing__user")
    serializer_class = PaymentSerializer
    permission_classes = [
        IsOwnerOrAdmin,
    ]


stripe.api_key = settings.STRIPE_API_KEY


@api_view(["POST"])
def create_payment_session(request, pk):
    borrowing = get_object_or_404(Borrowing, id=pk)
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": borrowing.book.daily_fee * 100,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:4242/success",
        cancel_url="http://127.0.0.1:8000/api/payments/cancel/",
    )

    payment = Payment.objects.create(
        status=Payment.PaymentStatusEnum.PENDING,
        type=Payment.PaymentTypeEnum.PAYMENT,
        borrowing=borrowing,
        session_id=session.id,
        session_url=session.url,
        money_to_pay=borrowing.book.daily_fee * 100,
    )
    payment.save()
    return Response({"message": session.url}, status=200)


@api_view(["GET"])
def cancel_payment(request):
    return Response({"message": "Payment was paused"}, status=200)
