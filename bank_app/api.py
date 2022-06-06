from rest_framework import generics
from rest_framework.response import Response
from .serializers import GetAccountSerializer
from .models import Account

class GetAccount(generics.ListCreateAPIView):
  def get(self, request):
    accounts = Account.objects.all()
    id = request.query_params.get("id")

    account = accounts.get(pk=id)
    serializer = GetAccountSerializer(account, many=False)
    return Response(data=serializer.data, status=200)