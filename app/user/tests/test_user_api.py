"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

    def test_token_valid_credentials_user_success(self):
        """Test generate token for valid credentials"""
        # create user in DB
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123'
        }
        create_user(**user_details)

        # test credentials
        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_token_invalid_credentials_user_error(self):
        """Test generate token for invalid credentials"""
        # create user in DB
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'correct-password'
        }
        create_user(**user_details)

        # test credentials
        payload = {
            'email': user_details['email'],
            'password': 'bad-password'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_token_empty_password_user_error(self):
        """Test generate token for empty password get error."""
        payload = {
            'email': 'test@example.com',
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrieve_me_unauthorized(self):
        """Test unauth user umable to access to me url"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    def setUp(self):
        self.user = {
            'email': 'test@example.com',
            'password': 'dummypass123',
            'name': 'Test Name'
        }
        self.client = APIClient()
        self.client.force_authenticate(user = self.user)

    def test_retrieve_me_authorized(self):
        """Test user with auth able to access me url"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.name, self.user['name'])
        self.assertEqual(res.data.email, self.user['email'])

    def test_post_me_not_allowed(self):
        """Test post request to me url not allowed"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test patch request to update user profile"""
        payload = {'name': 'Updated name', 'password': 'newPassword123'}

        res = self.client.patch(ME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
