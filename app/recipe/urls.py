
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe.views import RecipeAPI

router = DefaultRouter()
router.register('recipes', RecipeAPI)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]