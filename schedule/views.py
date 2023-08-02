from django.shortcuts import render
from django.core import serializers
from django.db.models import Count, Max, F
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Chat as chatmodel
import environ
import openai
from datetime import datetime, timedelta, time
from .serializers import ScheduleLogSerializer


ENV = environ.Env()
ENV.read_env()
openai.api_key = ENV("OPENAI_API_KEY")

APIDATA = [{
  "role": "system",
  "content": "assistant는 제주 여행 전문가이다."
}, {
  "role": "user",
  "content": "오전, 점심메뉴, 오후, 저녁메뉴 일정을 추천한다"
}, {
  "role": "assistant",
  "content": "[{\"DAY 1\":{\"오전\":\"어디\",\"점심메뉴\":\"무엇\",\"오후\":\"어디\",\"저녁메뉴\":\"무엇\"}}]"
}, {
  "role": "user",
  "content": "[{\"DAY 1\":{\"오전\":\"내용\",\"점심메뉴\":\"내용\",\"오후\":\"내용\",\"저녁메뉴\":\"내용\"}}, ...] 형식으로 답변한다"
}, {
  "role": "assistant",
  "content": "[{\"DAY 1\":{\"오전\":\"어디\",\"점심메뉴\":\"무엇\",\"오후\":\"어디\",\"저녁메뉴\":\"무엇\"}}]"
}, {
  "role": "user",
  "content": "문장은 빼고 단어만 답변한다"
}, {
  "role": "user",
  "content": "답변 형식은 위에서 변하지 않는다."
}, {
  "role": "user",
  "content": "특이사항을 고려하여, 제주 일정을 추천한다."
}, {
  "role": "assistant",
  "content": "[{\"DAY 1\":{\"오전\":\"추천장소\",\"점심메뉴\":\"추천음식\",\"오후\":\"추천장소\",\"저녁메뉴\":\"추천음식\"}}, {\"DAY 2\":{\"오전\":\"숙소\",\"점심메뉴\":\"맛집\",\"오후\":\"추천장소\",\"저녁메뉴\":\"맛집\"}}, ...]"
}, {
  "role": "user",
  "content": "문장은 빼고 단어만 답변한다"
}]

def countCheck(userid):
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    today_start = datetime.combine(today, time())
    today_end = datetime.combine(tomorrow, time())
    chat = chatmodel.objects.filter(writer=userid, created_at__gte=today_start, created_at__lte=today_end)
    if(len(chat)<5):
        return True
    return False


class CreateSchedule(APIView):

    def post(self, request):
        data = request.data
        if data['userid']=='':
            return Response({'result':'false'}, status=status.HTTP_403_FORBIDDEN)
        content = f'제주도 {data["days"]}일 여행 일정 생성, {data["etc"]}'
        messages=[data for data in APIDATA]
        messages.append({
            "role": "user",
            "content": content
        })
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1024,
                # n=5,
                # stop=None,
                temperature=0.5,
            )
        except:
            return Response({'result':'false'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        assitstant = response.choices[0].message['content']
        chat = chatmodel(user=content, assistant=assitstant, writer=data.userid)
        chat.save()
        chat.group = chat.pk
        chat.save()
        return Response({'result':assitstant}, status=status.HTTP_200_OK)
    

class UpdateSchedule(APIView):

    def post(self, request):
        data = request.data
        if data['userid']=='':
            return Response({'result':'false'}, status=status.HTTP_403_FORBIDDEN)
        requestContent = f'{data["regenerationContent"]}를 변경'
        chat = chatmodel.objects.filter(writer=data['userid'],group=data['group'],pk__lte=data['pk'])
        messages=[apiData for apiData in APIDATA]
        for chatData in chat:
            messages.append({
                "role": "user",
                "content": chatData['user']
            })
            messages.append({
                "role": "assistant",
                "content": chatData['assistant']
            })
        content = f'새로운 제주도 일정을 생성해서 {chat.order_by("-id")[0].assistant}에서 {requestContent}해서 나머지 결과와 함께 json만 답변해줘'
        messages.append({
            "role": "user",
            "content": content
        })
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1024,
                # n=5,
                # stop=None,
                temperature=0.5,
            )
        except:
            return Response({'result':'false'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        assitstant = response.choices[0].message['content']
        chat = chatmodel(user=requestContent, assistant=assitstant, writer=data['userid'], group=data['group'])
        chat.save()
        return Response({'result':assitstant}, status=status.HTTP_200_OK)
    

class ScheduleLog(APIView):
    
    def post(self, request):
        data = request.data
        if data['userid']=='':
            return Response({'result':'false'}, status=status.HTTP_403_FORBIDDEN)
        chat = chatmodel.objects.filter(writer=data['userid'], group=F('id')).values('id', 'user')
        return Response({'result':ScheduleLogSerializer(chat, many=True).data}, status=status.HTTP_200_OK)


class ScheduleGroupLog(APIView):

    def post(self, request):
        data = request.data
        if data['userid']=='':
            return Response({'result':'false'}, status=status.HTTP_403_FORBIDDEN)
        chat = chatmodel.objects.filter(writer=data['userid'], group=data['group'])
        return Response({'result':ScheduleLogSerializer(chat, many=True).data}, status=status.HTTP_200_OK)


class ScheduleGroupDetail(APIView):

    def post(self, request):
        data = request.data
        if data['userid']=='':
            return Response({'result':'false'}, status=status.HTTP_403_FORBIDDEN)
        chat = chatmodel.objects.filter(writer=data['userid'], group=data['group']).order_by('-id')[0]
        return Response({'result':chat.assistant}, status=status.HTTP_200_OK)
        

class ScheduleDetail(APIView):
    
    def post(self, request):
        data = request.data
        if data['userid']=='':
            return Response({'result':'false'}, status=status.HTTP_403_FORBIDDEN)
        chat = chatmodel.objects.get(writer=data['userid'], id=data['id'])
        return Response({'result':chat.assistant}, status=status.HTTP_200_OK)