"""
Tests for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email="test@example.com", password='testpass123'):
    """Helper function to create user"""
    return get_user_model().objects.create_user(email, password)


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

    def test_create_recipe(self):
        """Test user able to create recipe"""
        user = get_user_model().objects.create_user(
            'testuser@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tags(self):
        """Test create tags with particular user"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)
