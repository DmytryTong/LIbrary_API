import stripe
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing import helpers
from borrowing.models import Borrowing
from config import settings
from payment.helpers import calculate_fee_payment, calculate_fine_payment
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


@api_view(["POST"])
def create_payment_session(request, pk):
    stripe.api_key = settings.STRIPE_API_KEY
    borrowing = get_object_or_404(Borrowing, id=pk)

    fee = calculate_fee_payment(
        borrowing.expected_return_date,
        borrowing.borrow_date,
        borrowing.book.daily_fee
    )
    if borrowing.actual_return_date:
        fee = calculate_fine_payment(
            borrowing.expected_return_date,
            borrowing.actual_return_date,
            borrowing.book.daily_fee
        )

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": fee,
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
        money_to_pay=fee,
    )
    payment.save()

    payment_info = (
        f"Payment for book {borrowing.book.title}\n"
        f"User: {borrowing.user}\n"
        f"Status: {payment.status}\n"
        f"Amount: ${payment.money_to_pay / 100}"
    )
    helpers.send_telegram_notification(payment_info)

    return Response({"message": session.url}, status=200)


@api_view(["GET"])
def cancel_payment(request):
    return Response({"message": "Payment was paused"}, status=200)
