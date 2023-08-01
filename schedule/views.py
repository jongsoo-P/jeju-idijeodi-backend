from django.shortcuts import render
from rest_framework import APIView
import environ

ENV = environ.Env()
ENV.read_env()
OPENAI_API_KEY = ENV("OPENAI_API_KEY")

class Chat(APIView):

    def get(self, requset):
        pass

    def post(self, request):
        pass