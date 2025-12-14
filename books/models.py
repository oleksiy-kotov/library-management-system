from django.db import models


class Book(models.Model):
    class CoverBook(models.TextChoices):
        HARD = "hard", "Hard cover"
        SOFT = "soft", "Soft cover"

    title = models.CharField(max_length=255, unique=True, blank=False, null=False)
    author = models.CharField(max_length=255, blank=True, null=True)
    cover = models.CharField(choices=CoverBook, max_length=10, default=CoverBook.SOFT)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ["title", "author"]

    def __str__(self) -> str:
        return f"{self.title} - {self.author}"
