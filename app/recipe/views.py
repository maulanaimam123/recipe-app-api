"""
Views for Recipe APIs
"""
from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

from rest_framework import viewsets, authentication, permissions


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
