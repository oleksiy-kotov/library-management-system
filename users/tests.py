from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAPITestCase(APITestCase):
    def test_register_user(self):
        url = reverse("users:create")
        data = {"email": "newuser@test.com", "password": "strongpass123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@test.com").exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(email="exist@test.com", password="pass")
        data = {"email": "exist@test.com", "password": "pass"}
        response = self.client.post(reverse("users:create"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_me_authenticated(self):
        user = User.objects.create_user(email="me@test.com", password="pass")
        self.client.force_authenticate(user)
        response = self.client.get(reverse("users:manage"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "me@test.com")

    def test_update_me(self):
        user = User.objects.create_user(email="update@test.com", password="old")
        self.client.force_authenticate(user)
        data = {"first_name": "John", "last_name": "Doe"}
        response = self.client.patch(reverse("users:manage"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "John")
