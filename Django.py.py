!pip install django
!pip install djangorestframework

import os
from django.conf import settings
from django.db import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Destination
class Account(models.Model):
    email = models.EmailField(unique=True)
    account_id = models.CharField(unique=True, max_length=50)
    account_name = models.CharField(max_length=100)
    app_secret_token = models.CharField(max_length=100)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.account_name

class Destination(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    url = models.URLField()
    http_method = models.CharField(max_length=10)
    headers = models.JSONField()

    def __str__(self):
        return self.url


@api_view(['GET'])
def get_destinations(request, account_id):
    destinations = Destination.objects.filter(account__account_id=account_id)
    data = [{"url": dest.url, "http_method": dest.http_method, "headers": dest.headers} for dest in destinations]
    return Response(data)
#Visulization
import requests

@api_view(['POST'])
def incoming_data(request):
    if 'CL-X-TOKEN' not in request.headers:
        return Response({"error": "Unauthenticated"}, status=400)

    app_secret_token = request.headers['CL-X-TOKEN']
    account = Account.objects.filter(app_secret_token=app_secret_token).first()
    if not account:
        return Response({"error": "Invalid token"}, status=400)

    data = request.data
    destinations = Destination.objects.filter(account=account)
    for dest in destinations:
        if dest.http_method == 'GET':
            response = requests.get(dest.url, params=data, headers=dest.headers)
        elif dest.http_method in ['POST', 'PUT']:
            response = requests.request(dest.http_method, dest.url, json=data, headers=dest.headers)

    return Response({"message": "Data sent to destinations"})

#user give url
from django.urls import path
from .views import get_destinations, incoming_data

urlpatterns = [
    path('account/<str:account_id>/destinations/', get_destinations),
    path('server/incoming_data/', incoming_data),
]