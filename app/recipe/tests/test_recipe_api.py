"""
Tests for recipe APIs
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe
from serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def create_recipe(user, **params):
    """Create and return sample recipe"""
    default_options = {
        'title': 'Sample recipe here',
        'time_minutes': 25,
        'price':Decimal('10.00'),
        'description':'Sample description of recipe here',
        'link':'http://example.com/recipe.pdf',
    }
    default_options.update(params)

    recipe = Recipe.objects.create(user=user, **default_options)
    return recipe


class PublicRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required to call API"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'testuser@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test auth user list of recipe"""
        create_recipe(self.user)
        create_recipe(self.user)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test user should be able to see own recipe list"""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'dumypass123',
        )
        create_recipe(self.user)
        create_recipe(other_user)

        own_recipe = Recipe.objects.filter(user=self.user)
        res = self.client.get(RECIPES_URL)

        serializer = RecipeSerializer(own_recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

