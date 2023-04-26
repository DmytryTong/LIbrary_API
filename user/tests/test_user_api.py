from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from user.serializers import UserSerializer


class UserApiTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="testpass", bio="adasdadadaadadsadaa"
        )

    def test_create_user(self):
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertTrue(self.user.check_password("testpass"))

    def test_create_superuser(self):
        admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com", password="testpass"
        )
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_email_label(self):
        field_label = self.user._meta.get_field("email").verbose_name
        self.assertEqual(field_label, "email address")

    def test_username_is_none(self):
        self.assertIsNone(self.user.username)

    def test_bio_label(self):
        field_label = self.user._meta.get_field("bio").verbose_name
        self.assertEqual(field_label, "bio")

    def test_bio_max_length(self):
        max_length = self.user._meta.get_field("bio").max_length
        self.assertEqual(max_length, None)


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="testpass123",
        )

    def test_user_serializer(self):
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data["email"], "test@user.com")
