from rest_framework import viewsets

from books.models import Book
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    search_fields = ("title", "author")
    filter_fields = ("title", "author", "cover", "inventory")
