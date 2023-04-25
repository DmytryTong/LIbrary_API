from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from payment.models import Payment
from payment.permissions import IsOwnerOrAdmin
from payment.serializers import PaymentSerializer


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.select_related("borrowing__user")
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            return queryset.filter(borrowing__user=self.request.user)
        return queryset.all()


class PaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.select_related("borrowing__user")
    serializer_class = PaymentSerializer
    permission_classes = [IsOwnerOrAdmin, ]
