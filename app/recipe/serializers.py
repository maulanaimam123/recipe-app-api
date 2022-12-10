"""
Serializer for the user API View
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for user object"""
    pass