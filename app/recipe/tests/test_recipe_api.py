"""
Test for Recipe APIs
"""
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

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


def detail_url(recipe_id):
    """returns detail url for recipe api"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def recipe_image_upload_url(recipe_id):
    """returns url for upload image for recipe"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

def create_user(**params):
    """create rturn user"""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='test@user.com', password='test1234')
        self.client.force_authenticate(self.user)
    
    def test_list_recipes(self):
        """Test listing recipes"""

        sample_recipe(self.user)
        # sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all()
        serialized_recipe = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_recipe.data)
    
    def test_list_own_recipes_only(self):
        """Test only user's recipes returned in response"""
        other_user = create_user(email='other@user.com', password='test1234')

        sample_recipe(self.user)
        sample_recipe(user=other_user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serialized_recipe = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_recipe.data)
    
    def test_get_recipe_detail(self):
        """test get recipe detail API"""

        recipe = sample_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serialized_recipe = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serialized_recipe.data)
    
    def test_create_recipe(self):
        """Test creating recipe api"""

        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id = res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
    
    def test_partial_update(self):
        """test partial update of recipe"""
        original_link = "www.example.com/recipe.sf.sd"
        recipe = sample_recipe(
            user=self.user,
            title='SampleRecipe 2',
            link=original_link
        )
        
        payload = {'title':"Updated Recipe Title 4"}

        res = self.client.patch(detail_url(recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)
    
    def test_update(self):
        """Test full update put of recipe"""
        recipe = sample_recipe(
            title ="Sample title 6",
            user = self.user,
            time_minutes=10,
            link= "www.example.com/recipe.sf.sd",
            description="Sample respice for taste"
        )

        payload = {
            'title':"Sample title 6",
            'time_minutes':10,
            'link': "www.example.com/recipe.sf.sd",
            'description':"Sample respice for taste",
            'price':Decimal('46.22')
        }

        res = self.client.put(detail_url(recipe_id=recipe.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k,v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user,self.user)
    
    def test_update_recipe_user(self):
        """test updateing user of recipe"""
        new_user = create_user(email='asad@sdfsd.ax', password='asefzsdfa')
        recipe = sample_recipe(user=self.user)

        payload = {'user':new_user}
        self.client.patch(detail_url(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
    
    def test_create_recipe_with_tag(self):
        """testing create recipe including new tags"""
        payload = {
            'title':"Paneer butter masala",
            'price':Decimal('2.00'),
            'time_minutes':20,
            'tags':[{'name':'Veg'}, {'name':'Lunch'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            self.assertTrue(recipe.tags.filter(name=tag['name'], user=self.user).exists())

    def test_create_recipe_with_existing_tag(self):
        """testing create recipe with existing tag """
        tag1 = Tag.objects.create(name='Indian', user=self.user)

        payload = {
            'title':"Paneer butter masala",
            'price':Decimal('2.00'),
            'time_minutes':20,
            'tags':[{'name':'Indian'},{'name':"Italian"}]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        all_tags = Tag.objects.filter(user = self.user)
        self.assertEqual(all_tags.count(), 2)
        self.assertIn(tag1, all_tags.all())
        self.assertIn(tag1, recipe.tags.all())

    def test_create_tag_on_update_recipe(self):
        """Test create tag on updating recipe"""

        recipe = sample_recipe(user=self.user)

        payload = { 'tags': [{'name':'Lunch'}]}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag = Tag.objects.filter(user = self.user)
        self.assertEqual(tag.count(), 1)
        tag1 = tag[0]
        # recipes = Recipe.objects.filter(user = self.user)
        # self.assertEqual(recipes.count(), 1)
        # recipe = recipes[0]
        recipe.refresh_from_db()
        self.assertIn(tag1, recipe.tags.all())
    
    def test_replacing_tag_in_recipe(self):
        """test assigning tags to recipe with patch"""

        tag_bf = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(tag_bf)

        tag_ln = Tag.objects.create(user=self.user, name='Lunch')
        
        payload = {'tags':[{'name':'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_ln, recipe.tags.all())
        self.assertNotIn(tag_bf, recipe.tags.all())
    
    def test_removing_tag_in_recipe(self):
        """test removing tags to recipe with patch"""

        tag_sp = Tag.objects.create(user=self.user, name='Spicy')
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(tag_sp)

        payload = {'tags':[]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(tag_sp, recipe.tags.all())
        self.assertEqual(recipe.tags.count(), 0)

class ImageUploadTest(TestCase):
    """Testing image upload for recipe"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='test@user.com', password='test1234')
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)
    
    def tearDown(self):
        self.recipe.image.delete()
    
    def test_image_upload(self):
        """test image upload of recipe success"""
        url = recipe_image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10,10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image':image_file}
            res = self.client.post(url, payload, format='multipart')
        
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

        payload = {'image': 'something-wrong'}
        res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)