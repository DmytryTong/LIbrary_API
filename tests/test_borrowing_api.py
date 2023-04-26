from django.contrib.auth import get_user_model
from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing


BORROWING_URL = reverse("borrowing:borrowing-list")
BORROWING_URL_DETAIL = reverse("borrowing:borrowing-detail", kwargs={"pk": 1})
BORROWING_URL_CREATE = reverse("borrowing:borrowing-create")


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        """Test that authentication is required for borrowing API"""
        res = self.client.get(BORROWING_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authentication_required_detail(self):
        """Test that authentication is required for borrowing API"""
        res = self.client.get(BORROWING_URL_DETAIL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authentication_required_create(self):
        """Test that authentication is required for borrowing API"""
        res = self.client.post(BORROWING_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="testpass123",
        )
        self.client.force_authenticate(self.user)
        self.book = Book.objects.create(
            title="Test book",
            author="Test author",
            cover="Hard",
            inventory=10,
            daily_fee=100,
        )

    def test_retrieve_borrowings(self):
        """Test retrieving borrowings"""
        res = self.client.get(BORROWING_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_borrowings_detail(self):
        """Test retrieving borrowings"""
        borrowing_test = Borrowing.objects.create(
            user=self.user,
            book=Book.objects.create(
                title="Test book",
                author="Test author",
                cover="Hard",
                inventory=10,
                daily_fee=100,
            ),
            borrow_date="2021-01-01",
            expected_return_date="2021-01-08",
        )

        res = self.client.get(BORROWING_URL_DETAIL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], borrowing_test.id)


class AdminBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="adminpass123",
            is_staff=True,
        )
        self.simple_user = get_user_model().objects.create_user(
            email="test@user.com",
            password="testpass123",
        )
        self.client.force_authenticate(self.user)
        self.book = Book.objects.create(
            title="Test book",
            author="Test author",
            cover="Hard",
            inventory=10,
            daily_fee=100,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.simple_user,
            book=self.book,
            borrow_date="2021-01-01",
            expected_return_date="2021-01-08",
        )

    def test_all_borrowings(self):
        """Test retrieving all borrowings"""
        res = self.client.get(BORROWING_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_all_borrowings_detail(self):
        """Test retrieving all borrowings"""
        res = self.client.get(BORROWING_URL_DETAIL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], self.borrowing.id)
