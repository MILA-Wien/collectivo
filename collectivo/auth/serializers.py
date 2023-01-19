"""Serializers of the authentication module."""
from rest_framework import serializers


class TokenSerializer(serializers.Serializer):
    """A JWT Token."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, max_length=100)
