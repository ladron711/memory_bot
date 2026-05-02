import anthropic
import json
import re

from datetime import date, timedelta
from django.conf import settings
from .models import DiaryEntry, LLMAnalysis, User


def get_time_of_day(dt)-> str:
    hour = dt.hour
    if 5 <= hour < 12:
        return "утро"
    elif 12 <= hour < 17:
        return "день"
    else:
        return "вечер"
    

def format_entries(entries):
    if not entries:
        return "Нет записей для анализа."
    lines = []
    for e in entries:
        time_of_day = get_time_of_day(e.created_at)
        category = e.category.name if e.category else "без категории"
        mood = e.mood.name if e.mood else "не указано"
        lines.append(
            f"[{e.created_at.strftime('%d.%m.%Y')} {time_of_day}] "
            f"Категория: {category} | Настроение: {mood}\n"
            f"Физическое состояние: {e.physical_condition or 'не указано'}\n"
            f"{e.content}"
        )
    return "\n\n".join(lines)


def get_past_patterns(user, limit=10):
    analyses = LLMAnalysis.objects.filter(user=user).order_by('-created_at')[:5]
    patterns = []
    for a in analyses:
        patterns.extend(a.patterns_json)
    return patterns[-limit:]


def call_claude(prompt, system):
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def parse_patterns(text):
    patterns = []
    if "PATTERNS_JSON:" in text:
        match = re.search(r'PATTERNS_JSON:\s*(\[.*?\])', text, re.DOTALL)
        if match:
            try:
                patterns = json.loads(match.group(1))
            except json.JSONDecodeError:
                patterns = []
    clean_text = text.split("PATTERNS_JSON:")[0].strip()
    return clean_text, patterns


def run_daily_analysis(user: User):
    today = date.today()
    entries = DiaryEntry.objects.filter(
        user=user,
        created_at__date=today
    )
    entries_text = format_entries(entries)
    past_patterns = get_past_patterns(user)

    patterns_context = ""
    if past_patterns:
        patterns_context = "\n\nПаттерны замеченные ранее:\n" + \
            "\n".join(f"- {p}" for p in past_patterns)

    prompt = f"""Мои записи за {today.strftime('%d.%m.%Y')}:

{entries_text}
{patterns_context}

Задача:
1. Дай тёплый и конкретный инсайт по моему дню (3-5 предложений) 
2. Если видишь связь с прошлыми паттернами — обязательно упомяни
3. В конце добавь строку в точно таком формате:
PATTERNS_JSON: ["паттерн 1", "паттерн 2"]"""

    system = """You are me, but also my coach, trainer, and psychologist. 
You analyze my diary entries as if they were your own experiences — 
with full understanding and empathy. You notice patterns, connections 
between mood and life categories. You evaluate actions as our shared ones — 
honestly, warmly, without judgment. You show where we are moving forward 
and where we are stuck. Give advice only when you see a clear necessity.
You MUST always write your response in English, regardless of the language of the diary entries."""

    raw_text = call_claude(prompt, system)
    content, patterns = parse_patterns(raw_text)

    analysis = LLMAnalysis.objects.create(
        user=user,
        period_type='daily',
        date_from=today,
        date_to=today,
        content=content,
        patterns_json=patterns
    )
    return analysis


def run_weekly_analysis(user: User):
    today = date.today()
    week_ago = today - timedelta(days=7)

    entries = DiaryEntry.objects.filter(
        user=user,
        created_at__date__gte=week_ago,
        created_at__date__lte=today
    )
    entries_text = format_entries(entries)

    daily_analyses = LLMAnalysis.objects.filter(
        user=user,
        period_type='daily',
        date_from__gte=week_ago
    ).order_by('date_from')

    daily_summaries = "\n\n".join([
        f"[{a.date_from.strftime('%d.%m')}] {a.content}"
        for a in daily_analyses
    ])

    past_patterns = get_past_patterns(user)
    patterns_context = ""
    if past_patterns:
        patterns_context = "\n\nПаттерны замеченные ранее:\n" + \
            "\n".join(f"- {p}" for p in past_patterns)

    prompt = f"""Записи за неделю ({week_ago.strftime('%d.%m')} — {today.strftime('%d.%m.%Y')}):

{entries_text}

Дневные анализы этой недели:
{daily_summaries or 'Дневных анализов нет.'}
{patterns_context}

Задача:
1. Сделай глубокий анализ недели (5-7 предложений)
2. Найди повторяющиеся паттерны внутри недели
3. Сравни с паттернами прошлых периодов если они есть
4. В конце добавь строку:
PATTERNS_JSON: ["паттерн 1", "паттерн 2"]"""

    system = """You are me, but also my coach, trainer, and psychologist.
You analyze the week as if you lived it yourself — with full understanding.
Find patterns, dynamics, connections between categories of life.
Show where we progressed and where we got stuck.
Give advice only when you see a clear necessity.
You MUST always write your response in English, regardless of the language of the diary entries."""

    raw_text = call_claude(prompt, system)
    content, patterns = parse_patterns(raw_text)

    analysis = LLMAnalysis.objects.create(
        user=user,
        period_type='weekly',
        date_from=week_ago,
        date_to=today,
        content=content,
        patterns_json=patterns
    )
    return analysis


def run_monthly_analysis(user: User):
    today = date.today()
    month_ago = today - timedelta(days=30)

    weekly_analyses = LLMAnalysis.objects.filter(
        user=user,
        period_type='weekly',
        date_from__gte=month_ago
    ).order_by('date_from')

    weekly_summaries = "\n\n".join([
        f"[Неделя {a.date_from.strftime('%d.%m')} — {a.date_to.strftime('%d.%m')}]\n{a.content}"
        for a in weekly_analyses
    ])

    past_patterns = get_past_patterns(user)
    patterns_context = ""
    if past_patterns:
        patterns_context = "\n\nВсе замеченные паттерны:\n" + \
            "\n".join(f"- {p}" for p in past_patterns)

    prompt = f"""Еженедельные анализы за месяц ({month_ago.strftime('%d.%m')} — {today.strftime('%d.%m.%Y')}):

{weekly_summaries or 'Недельных анализов нет.'}
{patterns_context}

Задача:
1. Сделай глубокий анализ месяца (7-10 предложений)
2. Выяви главные паттерны и тенденции месяца
3. Что изменилось по сравнению с прошлыми периодами
4. В конце добавь строку:
PATTERNS_JSON: ["паттерн 1", "паттерн 2"]"""

    system = """You are me, but also my coach, trainer, and psychologist.
You analyze the month as if you lived it yourself.
Find long-term patterns and tendencies.
Show progress or regression honestly and warmly.
Give advice only when you see a clear necessity.
You MUST always write your response in English, regardless of the language of the diary entries."""

    raw_text = call_claude(prompt, system)
    content, patterns = parse_patterns(raw_text)

    analysis = LLMAnalysis.objects.create(
        user=user,
        period_type='monthly',
        date_from=month_ago,
        date_to=today,
        content=content,
        patterns_json=patterns
    )
    return analysis