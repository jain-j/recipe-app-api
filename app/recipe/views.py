"""
Recipe API ViewSet
"""

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe.serializers import RecipeSerializer,RecipeDetailSerializer,TagSerializer, IngredientSerializer, RecipeImageSerializer
from core.models import Recipe, Tag, Ingredient

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter('tags',OpenApiTypes.STR,
                            description="Comma separated list of tags id to filter recipe based on tags"),
            OpenApiParameter('ingredients',OpenApiTypes.STR,
                             description="Comma separated list of ingredients id to filter recipe based on tags")
        ]
    )
)
class RecipeAPI(viewsets.ModelViewSet):
    """Recipe API view set"""

    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_id_list(self, query_string):
        return [int(s) for s in query_string.split(',')]
    
    def get_queryset(self):
        # return self.queryset.filter(user=self.request.user)
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tags = self._params_to_id_list(tags)
            queryset = queryset.filter(tags__id__in=tags)
        if ingredients:
            ingredients = self._params_to_id_list(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients)
        
        return queryset.filter(user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        """return serializer class for request"""
        if self.action == 'list':
            return RecipeSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """create new recipe in model"""
        serializer.save(user = self.request.user)
    
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """upload recipe image"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter('assigned_only', OpenApiTypes.INT, enum=[0,1], description="Filter by recipe assignment")
        ]
    )
)
class BasicRecipeAttrViewSet(mixins.DestroyModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """"Base model for recipe attributes like tags and ingredients"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        assigned_only = bool(int(self.request.query_params.get('assigned_only', 0)))
        queryset = self.queryset
        
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        
        return self.queryset.filter(user = self.request.user).order_by("-name").distinct()


class TagAPI(BasicRecipeAttrViewSet):
    """API for tags"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientAPI(BasicRecipeAttrViewSet):
    """API view set for Ingredient of recipe"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
