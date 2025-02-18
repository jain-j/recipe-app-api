
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe.views import RecipeAPI,TagAPI, IngredientAPI

router = DefaultRouter()
router.register('recipes', RecipeAPI)
router.register('tags', TagAPI)
router.register('ingredients', IngredientAPI)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]