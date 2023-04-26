from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from payment.models import Payment
from borrowing.models import Borrowing
from book.models import Book
from payment.serializers import PaymentSerializer


PAYMENT_LIST_URL = reverse("payments:payment-list")


class UserPaymentsApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testuser@testlibrary.com",
            "password1122",
        )
        self.useradmin = get_user_model().objects.create_superuser(
            "testuser2@testlibrary.com",
            "password1122",
        )
        self.test_book = Book.objects.create(
                title="Test book",
                author="Test author",
                cover="Hard",
                inventory=10,
                daily_fee=10,
        )
    
    def test_auth_required(self) -> None:
        response = self.client.get(PAYMENT_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_confirmed(self) -> None:
        self.client.force_authenticate(self.user)
        response = self.client.get(PAYMENT_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_owner_gets_payments(self) -> None:
        self.client.force_authenticate(self.user)
        test_payment1 = Payment.objects.create(
            status=Payment.PaymentStatusEnum.PENDING,
            type=Payment.PaymentTypeEnum.PAYMENT,
            borrowing=Borrowing.objects.create(
                user=self.user,
                book=self.test_book,
                borrow_date="2021-01-01",
                expected_return_date="2021-01-08",
            ),
            session_id="XxxxxXXXxx",
            session_url="http://testest.io",
            money_to_pay=100,
        )
        test_payment2 = Payment.objects.create(
            status=Payment.PaymentStatusEnum.PENDING,
            type=Payment.PaymentTypeEnum.PAYMENT,
            borrowing=Borrowing.objects.create(
                user=self.user,
                book=self.test_book,
                borrow_date="2021-01-01",
                expected_return_date="2021-01-08",
            ),
            session_id="XxxxxXXXxx",
            session_url="http://testest.io",
            money_to_pay=100,
        )
        test_payment3 = Payment.objects.create(
            status=Payment.PaymentStatusEnum.PENDING,
            type=Payment.PaymentTypeEnum.PAYMENT,
            borrowing=Borrowing.objects.create(
                user=self.useradmin,
                book=self.test_book,
                borrow_date="2021-01-01",
                expected_return_date="2021-01-08",
            ),
            session_id="XxxxxXXXxx",
            session_url="http://testest.io",
            money_to_pay=100,
        )

        response = self.client.get(PAYMENT_LIST_URL)

        serializer1 = PaymentSerializer(test_payment1)
        serializer2 = PaymentSerializer(test_payment2)
        serializer3 = PaymentSerializer(test_payment3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)
    
    def test_admin_gets_payments(self) -> None:
        self.client.force_authenticate(self.useradmin)
        test_payment1 = Payment.objects.create(
            status=Payment.PaymentStatusEnum.PENDING,
            type=Payment.PaymentTypeEnum.PAYMENT,
            borrowing=Borrowing.objects.create(
                user=self.user,
                book=self.test_book,
                borrow_date="2021-01-01",
                expected_return_date="2021-01-08",
            ),
            session_id="XxxxxXXXxx",
            session_url="http://testest.io",
            money_to_pay=100,
        )
        test_payment2 = Payment.objects.create(
            status=Payment.PaymentStatusEnum.PENDING,
            type=Payment.PaymentTypeEnum.PAYMENT,
            borrowing=Borrowing.objects.create(
                user=self.user,
                book=self.test_book,
                borrow_date="2021-01-01",
                expected_return_date="2021-01-08",
            ),
            session_id="XxxxxXXXxx",
            session_url="http://testest.io",
            money_to_pay=100,
        )
        test_payment3 = Payment.objects.create(
            status=Payment.PaymentStatusEnum.PENDING,
            type=Payment.PaymentTypeEnum.PAYMENT,
            borrowing=Borrowing.objects.create(
                user=self.useradmin,
                book=self.test_book,
                borrow_date="2021-01-01",
                expected_return_date="2021-01-08",
            ),
            session_id="XxxxxXXXxx",
            session_url="http://testest.io",
            money_to_pay=100,
        )

        response = self.client.get(PAYMENT_LIST_URL)

        serializer1 = PaymentSerializer(test_payment1)
        serializer2 = PaymentSerializer(test_payment2)
        serializer3 = PaymentSerializer(test_payment3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertIn(serializer3.data, response.data)
