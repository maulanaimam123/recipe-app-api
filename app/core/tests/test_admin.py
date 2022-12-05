"""
Tests for admin page functionalities
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTest(TestCase):
    """Test for Django admin site"""

    def setUp(self):
        """Create users and client"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_login(self.admin_user)
        self.normal_user = get_user_model().objects.create_user(
            email='user@example.com',
            password='userpass123',
            name='Test user'
        )

    def test_user_list(self):
        """Test that users are listed on the page"""
        url = reverse('admin:core_user_changelist') #getting url of django admin
        res = self.client.get(url)

        self.assertContains(res, self.normal_user.email)
        self.assertContains(res, self.normal_user.name)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        url = reverse('admin:core_user_change', args=[self.normal_user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
