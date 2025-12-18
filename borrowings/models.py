from django.db import models

from books.models import Book
from library_management_system import settings


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    class Meta:
        verbose_name = "Borrowing"
        verbose_name_plural = "Borrowings"
        ordering = ("borrow_date",)

    def __str__(self):
        return f"Book: {self.book.title} - Reader: {self.user.username}"
