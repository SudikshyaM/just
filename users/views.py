from django.shortcuts import render
from rest_framework import generics,permissions,mixins,status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


@csrf_exempt
def signup(request):
    if request.method=="POST":
        try:
            data=JSONParser().parse(request)
            user=User.objects.create_user(username=data['username'],email=data['email'],password=data['password'])
            user.save()

            token=Token.objects.create(user=user)
            return JsonResponse({'token':str(token)},status=status.HTTP_200_OK)
        except IntegrityError:
            return JsonResponse({'error':'Username is already taken,try another'},status=400)
        
@csrf_exempt
def login(request):
    if request.method=="POST":
        data=JSONParser().parse(request)
        user=authenticate(request,username=data['username'],password=data['password'])
        if user is None:
            return JsonResponse({'error':'username and password didnot match'},status=400)
        else:
            if user.is_staff:
                return JsonResponse({'token': str(Token.objects.get(user=user)), 'redirect': '/admin-page/'}, status=200)
            else:
                try:
                  token=Token.objects.get(user=user)
                except:
                  token=Token.objects.create(user=user)
                return JsonResponse({'token': str(token), 'user': {'_id':user.id}}, status=200)