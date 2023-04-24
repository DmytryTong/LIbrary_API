from rest_framework import generics, permissions

from .models import Borrowing
from .serializers import BorrowingSerializer


class BorrowingListView(generics.ListCreateAPIView):
    serializer_class = BorrowingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = Borrowing.objects.all()
            user_id = self.request.query_params.get("user_id", None)
            if user_id is not None:
                queryset = queryset.filter(user__id=user_id)
        else:
            queryset = Borrowing.objects.filter(user=user)
        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            queryset = queryset.filter(actual_return_date__isnull=True)
        return queryset


class BorrowingDetailView(generics.RetrieveAPIView):
    serializer_class = BorrowingSerializer
    queryset = Borrowing.objects.all()
    permission_classes = [permissions.IsAuthenticated]
