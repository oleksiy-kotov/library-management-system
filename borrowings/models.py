from datetime import date

from django.db import models

from books.models import Book
from library_management_system import settings


class Borrowing(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("returned", "Returned"),
        ("overdue", "Overdue"),
    ]
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")

    class Meta:
        verbose_name = "Borrowing"
        verbose_name_plural = "Borrowings"
        ordering = ("borrow_date",)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"

    def save(self, *args, **kwargs):
        if self.actual_return_date:
            self.status = "returned"
        elif self.expected_return_date < date.today():
            self.status = "overdue"
        else:
            self.status = "active"
        super().save(*args, **kwargs)
