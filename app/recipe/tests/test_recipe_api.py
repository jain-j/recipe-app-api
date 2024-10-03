"""
Test for Recipe APIs
"""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')

def sample_recipe(user, **params):
    """create sample recipe object for testing"""

    default = {
        'title' : 'Sample Recipe 121',
        'time_minutes' : 22,
        'price' : Decimal('22.5'),
        'description' : 'Description for Sample recipe 1',
        'link' : 'http://asd.sda.asd.ad/asd.as'
    }

    default.update(params)

    recipe = Recipe.objects.create(user = user, **default)
    return recipe

class PublicRecipeApiTests(TestCase):
    """Tests Recipe API unauthenticated"""

    def setUp(self):
        self.client = APIClient()
    
    def test_api_without_auth(self):
        """Tests API without authenticating"""

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTest(TestCase):
    """Tests Recipe API authenticated"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('test@user.com', 'test1234')
        self.client.force_authenticate(self.user)
    
    def test_list_recipes(self):
        """Test listing recipes"""

        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all()
        serialized_recipe = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_recipe.data)
    
    def test_list_own_recipes_only(self):
        """Test only user's recipes returned in response"""
        other_user = get_user_model().objects.create_user('other@user.com', 'test1234')

        sample_recipe(self.user)
        sample_recipe(user=other_user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serialized_recipe = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_recipe.data)