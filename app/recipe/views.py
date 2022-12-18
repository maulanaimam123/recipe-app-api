"""
Views for Recipe APIs
"""
from core.models import (
    Recipe,
    Tag,
    Ingredient,
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer,
)

from rest_framework import (
    viewsets,
    authentication,
    permissions,
    mixins,
)


class RecipeViewset(viewsets.ModelViewSet):
    """View for manage Recipe APIs"""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Function to retrieve recipe list for auth user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Method to define serializer for endpoint action"""
        if (self.action == 'list'):
            return RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create new recipe, link with current user"""
        serializer.save(user=self.request.user)


class BaseRecipeAttrViewset(
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Override to filter by user-id"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewset):
    """Manage tags in the database"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewset):
    """Manage ingredients in the database"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
