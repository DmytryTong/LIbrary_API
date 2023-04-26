import stripe
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing import helpers
from borrowing.models import Borrowing
from config import settings
from payment.helpers import calculate_fee_payment
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


def create_payment_session(request, pk):
    stripe.api_key = settings.STRIPE_API_KEY
    borrowing = get_object_or_404(Borrowing, id=pk)

    if borrowing.actual_return_date:
        fee = calculate_fee_payment(
            borrowing.expected_return_date,
            borrowing.actual_return_date,
            borrowing.book.daily_fee
        ) * settings.FINE_MULTIPLIER
    else:
        fee = calculate_fee_payment(
            borrowing.borrow_date,
            borrowing.expected_return_date,
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
        success_url=request.build_absolute_uri(reverse("payments:success-payment")) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse("payments:cancel-payment")),
    )

    payment = Payment.objects.create(
        status=Payment.PaymentStatusEnum.PENDING,
        type=Payment.PaymentTypeEnum.PAYMENT,
        borrowing=borrowing,
        session_id=session.id,
        session_url=session.url,
        money_to_pay=fee,
    )

    if borrowing.actual_return_date:
        payment.type = Payment.PaymentTypeEnum.FINE
    payment.save()

    payment_info = (
        f"{payment.type} for book {borrowing.book.title}\n"
        f"User: {borrowing.user}\n"
        f"Status: {payment.status}\n"
        f"Amount: ${payment.money_to_pay / 100}"
    )
    helpers.send_telegram_notification(payment_info)

    return session.url


@api_view(["GET"])
def cancel_payment(request) -> Response:
    return Response({"message": "Payment was paused"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def success_payment(request) -> Response:
    payment = get_object_or_404(Payment, session_id=request.GET.get("session_id"))
    payment.status=Payment.PaymentStatusEnum.PAID
    payment.save()
    return Response({"message": (
        f"Thank you {payment.borrowing.user}, your payment is successful! "
        f"Your payment number is {payment.id} "
        "Link: " + request.build_absolute_uri(reverse("payments:payment-detail", args=[payment.id]))
    )}, status=status.HTTP_200_OK)
