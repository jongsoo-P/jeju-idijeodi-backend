from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from .serializers import UserSerializer
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout
import environ

env = environ.Env()


class Registration(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            return Response({'message':'login'}, status=status.HTTP_400_BAD_REQUEST)
        form = RegisterForm(request.data)
        if form.is_valid():
            user = form.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

class Login(APIView):
    def post(self, request):
        form = LoginForm(request, request.data)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=email, password=password)
            if user:
                # login(request, user)
                return Response({'email':email}, status=status.HTTP_202_ACCEPTED)
        return Response({'message':'email 또는 password를 확인해주세요'}, status=status.HTTP_400_BAD_REQUEST)
    

class Logout(APIView):
    def get(self, request):
        # logout(request)
        return Response({'meesage':'logout'}, status=status.HTTP_200_OK)