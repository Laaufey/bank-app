from rest_framework import serializers
from .models import Account


class GetAccountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "title",
        )
        model = Account
