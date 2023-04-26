from unittest import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

from book.models import Book

BOOK_URL = reverse("book:book-list")

DATA = {
    "title": "test_title",
    "author": "test_author",
    "cover": "Hard",
    "inventory": 5,
    "daily_fee": Decimal(10),
}


class AuthorizeBookViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            "test@test.com", "test", is_staff=False
        )
        self.client.force_authenticate(self.user)
        self.book = Book.objects.create(
            title="Test Book", author="Test Author", cover=Book.BookCoverChoices.HARD,
            inventory=5, daily_fee=Decimal(10)
        )
        self.detail_url = reverse("book:book-detail", args=[self.book.pk])

    def test_non_admin_put_request(self) -> None:
        data = {"title": "New Title"}
        response = self.client.put(self.detail_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_delete_request(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AnonBookViewTest(APITestCase):

    def test_anon_post_request(self) -> None:
        response = self.client.post(BOOK_URL, data=DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminBookViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            "test1@test.com", "test1", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_admin_post_request(self) -> None:
        response = self.client.post(BOOK_URL, data=DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BookModelTest(TestCase):
    def test_str_method(self):
        book = Book.objects.create(
            title="Test Book", author="Test Author", cover=Book.BookCoverChoices.HARD,
            inventory=5, daily_fee=Decimal(10)
        )
        self.assertEqual(str(book), "Test Book")
