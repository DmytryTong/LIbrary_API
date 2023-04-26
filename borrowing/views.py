import django_filters
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from book.models import Book
from .filters import BorrowingFilter
from .models import Borrowing
from .permissions import IsOwnerOrAdmin
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
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.filter(user=user)
        is_active = self.request.query_params.get("is_active", None)
        user_id = self.request.query_params.get("user_id", None)
        if is_active is not None:
            is_active = True if is_active.lower() == "true" else False
            queryset = (
                queryset.filter(actual_return_date=None)
                if is_active
                else queryset.exclude(actual_return_date=None)
            )
        if user.is_superuser and user_id is not None:
            queryset = Borrowing.objects.filter(user_id=user_id)
        return queryset


class BorrowingDetailView(generics.RetrieveAPIView):
    serializer_class = BorrowingSerializer
    queryset = Borrowing.objects.all()
    permission_classes = [IsOwnerOrAdmin, ]


class BorrowingCreateView(generics.CreateAPIView):
    serializer_class = BorrowingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        book_id = request.data.get("book")
        book = get_object_or_404(Book, id=book_id)

        if book.inventory <= 0:
            return Response(
                {"error": "Book is not available"}, status=status.HTTP_400_BAD_REQUEST
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
            book_title = borrowing.book.title
            user_email = borrowing.user.email
            borrowing_id = borrowing.id
            message = (
                f"New borrowing created:\n"
                f"Book: {book_title}\n"
                f"User: {user_email}\n"
                f"Borrowing ID: {borrowing_id}"
            )
            send_telegram_notification(message)

            return Response(
                {"message": "your link to pay --->  " + payment_url},
                status=status.HTTP_201_CREATED
            )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
