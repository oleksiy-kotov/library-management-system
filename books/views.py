from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication

from books.models import Book
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    authentication_classes = (JWTAuthentication,)

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("title", "author")

    filterset_fields = ("cover",)
    ordering_fields = ["title", "author", "inventory", "daily_fee"]
    ordering = ["title", "author"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
