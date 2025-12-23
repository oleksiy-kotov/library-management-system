from datetime import date, timedelta

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from borrowings.filters import BorrowingFilter
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer
from library_management_system.utils.telegram_helper import send_telegram_notification


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_class = BorrowingFilter
    search_fields = ("user__username", "book__title")
    ordering_fields = ("expected_return_date", "borrow_date")

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return queryset
            else:
                return queryset.filter(user=self.request.user)
        else:
            return Borrowing.objects.none()

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        if book.inventory <= 0:
            raise serializers.ValidationError("No copies available")

        book.inventory -= 1
        book.save()

        if "expected_return_date" not in serializer.validated_data:
            serializer.validated_data["expected_return_date"] = (
                date.today() + timedelta(days=7)
            )
        borrowing = serializer.save(user=self.request.user)

        message = (
            f"New borrowing created!\n"
            f"User: {self.request.user.email} ({self.request.user.full_name})\n"
            f"Book: {book.title} by {book.author}\n"
            f"Borrow date: {borrowing.borrow_date}\n"
            f"Expected return: {borrowing.expected_return_date}\n"
            f"Status: {borrowing.status}"
        )
        send_telegram_notification(message)

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            return Response(
                {"detail": "Already returned"}, status=status.HTTP_400_BAD_REQUEST
            )
        borrowing.actual_return_date = date.today()
        borrowing.save()

        borrowing.book.inventory += 1
        borrowing.book.save()
        return Response(
            {"detail": "Book returned successfully"}, status=status.HTTP_200_OK
        )
