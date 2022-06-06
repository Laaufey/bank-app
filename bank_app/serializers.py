from rest_framework import serializers
from .models import Account, Ledger


class GetAccountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "title",
        )
        model = Account

class ExternalTransferSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Ledger
