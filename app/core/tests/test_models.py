"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_success(self):
        """Test user creation using email and password"""
        email = 'test@example.com'
        password = 'testpassword123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_normalize_email(self):
        """Test email normalization for new users"""
        sample_emails = [
            ['test1@example.com', 'test1@example.com'],
            ['Test2@EXAMPLE.COM', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(
                email,
                'dummypassword123'
            )
            self.assertEqual(user.email, expected_email)

    def test_create_user_without_email_raises_error(self):
        """Test user creation without email/null will result in ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'dummypassword123')

    def test_create_superuser(self):
        """Test for superuser creation support"""
        user = get_user_model().objects.create_superuser(
            email='test@example.com',
            password='dummypassword123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
