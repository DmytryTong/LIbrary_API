import django_filters
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from book.models import Book
from payment.models import Payment
from .filters import BorrowingFilter
from .models import Borrowing
from .permissions import IsBorrowingOwnerOrAdmin
from .serializers import BorrowingSerializer, BorrowingCreateSerializer
from .helpers import send_telegram_notification
from payment.views import create_payment_session


class BorrowingReturnView(generics.UpdateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            return Response(
                {"error": "This borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.actual_return_date = timezone.now()
        borrowing.is_active = False
        borrowing.save()
        borrowing.book.inventory += 1
        borrowing.book.save()

        if borrowing.actual_return_date > borrowing.expected_return_date:
            payment_url = create_payment_session(request, borrowing.id)
            return Response(
                {"message": "your link to pay ---> " + payment_url},
                status=status.HTTP_201_CREATED
            )

        serializer = self.get_serializer(borrowing)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class BorrowingListView(generics.ListAPIView):
    serializer_class = BorrowingSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = BorrowingFilter
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        queryset = Borrowing.objects.all()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            is_active = True if is_active.lower() == "true" else False
            queryset = (
                queryset.filter(actual_return_date=None)
                if is_active
                else queryset.exclude(actual_return_date=None)
            )
        return queryset


class BorrowingDetailView(generics.RetrieveAPIView):
    serializer_class = BorrowingSerializer
    queryset = Borrowing.objects.all()
    permission_classes = [IsBorrowingOwnerOrAdmin, ]


class BorrowingCreateView(generics.CreateAPIView):
    serializer_class = BorrowingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        # Check if user has any pending payments
        if Payment.objects.filter(
                borrowing__user=user,
                status=Payment.PaymentStatusEnum.PENDING
        ).exists():
            borrowing_list_url = reverse("borrowing:borrowing-list")
            return Response(
                {
                    "ERROR": f"Cannot create a borrowing until all pending payments are cleared. "
                             f"Please pay all pending payments before creating a new borrowing. "
                             f"You can view your borrowings at {borrowing_list_url}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        book_id = request.data.get("book")
        book = get_object_or_404(Book, id=book_id)

        if book.inventory <= 0:
            return Response(
                {"ERROR": "Book is not available"}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            book.inventory -= 1
            book.save()

            user = request.user

            borrowing = Borrowing.objects.create(
                book=book,
                user=user,
                borrow_date=request.data.get("borrow_date"),
                expected_return_date=request.data.get("expected_return_date"),
            )

            serializer = BorrowingSerializer(borrowing)
            payment_url = create_payment_session(request, borrowing.id)

            # Send a notification to the Telegram chat
            message = f"A new borrowing has been created:\n\n{serializer.data}"
            send_telegram_notification(message)

            return Response(
                {"message": "your link to pay --->  " + payment_url},
                status=status.HTTP_201_CREATED
            )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
