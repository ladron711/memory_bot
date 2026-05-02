from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Category, Mood, DiaryEntry
from .serializers import DiaryEntrySerializer

from .analysis import run_daily_analysis, run_weekly_analysis, run_monthly_analysis


class CreateDiaryEntryView(APIView):

    def post(self, request):
        telegram_id = request.data.get("telegram_id")
        username = request.data.get("username")
        cat_name = request.data.get("category")
        mood_name = request.data.get("mood") 
        condition = request.data.get("physical_condition")
        content = request.data.get("content")

        user, _ = User.objects.get_or_create(telegram_id=telegram_id, defaults={"username": username})

        category = Category.objects.filter(name=cat_name).first() if cat_name else None
        mood = Mood.objects.filter(name=mood_name).first() if mood_name else None

        entry = DiaryEntry.objects.create(
            user=user,
            category=category,
            mood=mood,
            physical_condition=condition,
            content=content,
        )

        serializer = DiaryEntrySerializer(entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RunAnalysisView(APIView):
    def post(self, request):
        analysis_type = request.data.get("type")  # daily, weekly, monthly
        telegram_id = request.data.get("telegram_id")

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if analysis_type == "daily":
            analysis = run_daily_analysis(user)
        elif analysis_type == "weekly":
            analysis = run_weekly_analysis(user)
        elif analysis_type == "monthly":
            analysis = run_monthly_analysis(user)
        else:
            return Response({"error": "Invalid type"}, status=400)

        return Response({"content": analysis.content})
    
# Create your views here.
