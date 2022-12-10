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
from recipe.serializers import (
    RecipeSerializer, RecipeDetailSerializer
)

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])

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

    def test_get_recipe_details(self):
        """Test get detail of recipe"""
        recipe = create_recipe(self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(serializer.data, res.data)

    def test_create_recipe(self):
        """Test create recipe"""
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'link': 'www.test.com/recipe.pdf',
            'description': 'there are 4 steps to create...',
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data.user, self.user)
        recipe = Recipe.objects.filter(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(v, getattr(recipe, k))
