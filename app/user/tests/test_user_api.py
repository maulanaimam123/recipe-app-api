"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'dummypass123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # check user creation response success
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # check user password valid
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

        # check response dont contain password - security reason
        self.assertNotIn(payload['password'], res.data)

    def test_create_user_with_existing_email_error(self):
        """Test creating a user using existing email generate error"""
        payload = {
            'email': 'test@example.com',
            'password': 'dummypass123',
            'name': 'Test Name',
        }
        # simulate user creation - exists in DB
        create_user(**payload)

        # new user request with existing email - error
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test error should return when password is less than 5 char"""
        payload = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)





