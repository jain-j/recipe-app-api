"""
Tests for TAG APIs
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def create_user(email = "test@example.com", password = "test@123"):
    """create and return user"""
    return get_user_model().objects.create_user(email = email, password = password)

def detail_url(tag_id):
    """gives url for detail page"""
    return reverse("recipe:tag-detail", args=[tag_id])

class PublicTagApiTests(TestCase):
    """Tag API testing unathenticated"""

    def setUp(self):
        self.client = APIClient()
    
    def test_api_without_auth(self):
        """test list tag api unauthenticated"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagApiTests(TestCase):
    """Test Tag Api"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
    
    def test_tag_list(self):
        """Test Tag list api"""
        Tag.objects.create(user = self.user, name = "Italian")
        Tag.objects.create(user = self.user, name = "Mexican")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serialized_tags = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized_tags.data)
    
    def test_tag_list_user_limited(self):
        """Test tag list is limited to user"""
        unauth_user = create_user(email = "test2@example2.com")

        Tag.objects.create(user = unauth_user, name = "Italian")
        tag = Tag.objects.create(user = self.user, name = "Mexican")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_tag_update(self):
        """Test patch/update of tag api"""
        tag = Tag.objects.create(user = self.user, name = "Post Meal")

        payload = {"name":"Dessert"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])
    
    def test_tag_delete(self):
        """test delete tag api"""

        tag = Tag.objects.create(user = self.user, name = "Spicy")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
