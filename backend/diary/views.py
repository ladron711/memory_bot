from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Category, Mood, DiaryEntry
from .serializers import DiaryEntrySerializer


class CreateDiaryEntryView(APIView):

    def post(self, request):
        telegram_id = request.data.get("telegram_id")
        username = request.data.get("username")
        cat_name = request.data.get("category")
        mood_name = request.data.get("mood")
        sleep = request.data.get("sleep_quality")   
        condition = request.data.get("physical_condition")
        content = request.data.get("content")

        user, _ = User.objects.get_or_create(telegram_id=telegram_id, defaults={"username": username})

        category = Category.objects.filter(name=cat_name).first() if cat_name else None
        mood = Mood.objects.filter(name=mood_name).first() if mood_name else None

        entry = DiaryEntry.objects.create(
            user=user,
            category=category,
            mood=mood,
            sleep_quality=sleep,
            physical_condition=condition,
            content=content,
        )

        serializer = DiaryEntrySerializer(entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    
# Create your views here.
