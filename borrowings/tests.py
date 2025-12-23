# borrowings/tests.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from books.models import Book
from borrowings.models import Borrowing
from datetime import date, timedelta

User = get_user_model()


class BorrowingAPITestCase(APITestCase):
    def setUp(self):
        # Тільки користувачі — вони не змінюються
        self.admin = User.objects.create_superuser(
            email="admin@test.com", password="admin"
        )
        self.user = User.objects.create_user(email="user@test.com", password="user123")

    def test_create_borrowing(self):
        book = Book.objects.create(
            title="Test Book", author="Author", inventory=3, daily_fee=1.00
        )
        self.client.force_authenticate(self.user)
        data = {
            "book_id": book.id,
            "expected_return_date": (date.today() + timedelta(days=10)).isoformat(),
        }
        response = self.client.post(reverse("borrowings:borrowing-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 1)
        book.refresh_from_db()
        self.assertEqual(book.inventory, 2)

    def test_create_borrowing_no_copies(self):
        book = Book.objects.create(
            title="Empty Book", author="Author", inventory=0, daily_fee=1.00
        )
        self.client.force_authenticate(self.user)
        data = {"book_id": book.id}
        response = self.client.post(reverse("borrowings:borrowing-list"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_borrowings_user_sees_only_own(self):
        book = Book.objects.create(
            title="Shared Book", author="Author", inventory=3, daily_fee=1.00
        )
        Borrowing.objects.create(
            book=book,
            user=self.user,
            expected_return_date=date.today() + timedelta(days=7),
        )
        Borrowing.objects.create(
            book=book,
            user=self.admin,
            expected_return_date=date.today() + timedelta(days=5),
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("borrowings:borrowing-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # тільки своя

    def test_admin_sees_all_borrowings(self):
        book = Book.objects.create(
            title="Admin Book", author="Author", inventory=3, daily_fee=1.00
        )
        Borrowing.objects.create(
            book=book,
            user=self.user,
            expected_return_date=date.today() + timedelta(days=7),
        )
        Borrowing.objects.create(
            book=book,
            user=self.admin,
            expected_return_date=date.today() + timedelta(days=5),
        )

        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse("borrowings:borrowing-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_return_book(self):
        book = Book.objects.create(
            title="Return Book", author="Author", inventory=2, daily_fee=1.00
        )
        borrowing = Borrowing.objects.create(
            book=book,
            user=self.user,
            expected_return_date=date.today() + timedelta(days=7),
        )

        self.client.force_authenticate(self.user)
        url = reverse("borrowings:borrowing-return-book", kwargs={"pk": borrowing.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)
        self.assertEqual(borrowing.status, "returned")

        book.refresh_from_db()
        self.assertEqual(book.inventory, 3)  # +1 після повернення

    def test_filter_is_active(self):
        book = Book.objects.create(
            title="Filter Book", author="Author", inventory=3, daily_fee=1.00
        )
        # Активна позичка
        Borrowing.objects.create(
            book=book,
            user=self.user,
            expected_return_date=date.today() + timedelta(days=7),
        )
        # Повернена позичка
        Borrowing.objects.create(
            book=book,
            user=self.user,
            expected_return_date=date.today() - timedelta(days=1),
            actual_return_date=date.today(),
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse("borrowings:borrowing-list") + "?is_active=true"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # тільки активна
