from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from book.models import Book
from book.permissions import IsAdminOrIfAuthenticatedReadOnly
from book.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminOrIfAuthenticatedReadOnly,)
