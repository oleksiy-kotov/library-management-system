from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Book

User = get_user_model()


class BookAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@test.com", password="admin123"
        )
        self.user = User.objects.create_user(email="user@test.com", password="user123")

        self.book1 = Book.objects.create(
            title="1984",
            author="George Orwell",
            cover="hard",
            inventory=5,
            daily_fee=1.99,
        )
        self.book2 = Book.objects.create(
            title="To Kill a Mockingbird",
            author="Harper Lee",
            cover="soft",
            inventory=0,
            daily_fee=0.99,
        )

    def test_list_books_unauthenticated(self):
        response = self.client.get(reverse("books:book-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_book(self):
        response = self.client.get(
            reverse("books:book-detail", kwargs={"pk": self.book1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "1984")

    def test_create_book_as_admin(self):
        self.client.force_authenticate(self.admin)
        data = {
            "title": "New Book",
            "author": "Author",
            "cover": "soft",
            "inventory": 10,
            "daily_fee": 2.50,
        }
        response = self.client.post(reverse("books:book-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)

    def test_create_book_as_user_forbidden(self):
        self.client.force_authenticate(self.user)
        data = {"title": "Forbidden Book", "author": "Me", "inventory": 1}
        response = self.client.post(reverse("books:book-list"), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
