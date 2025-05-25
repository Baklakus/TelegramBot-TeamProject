import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from .models import Survey, Question, AnswerOption, Response, ResponseSession, Respondent
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.views.decorators.http import require_POST
@login_required
def index(request):
    surveys = Survey.objects.all().order_by('-created_at')
    return render(request, 'main/index.html', {'surveys': surveys})


@require_http_methods(["GET", "POST"])  # Разрешаем GET и POST
def create_survey(request):
    if request.method == "GET":
        return render(request, "main/create_survey.html")

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title")
            description = data.get("description", "")
            questions = data.get("questions", [])

            if not title:
                return JsonResponse({"error": "Название опроса обязательно"}, status=400)

            survey = Survey.objects.create(title=title, description=description)
            for q in questions:
                is_required = q.get("required", False)
                question = Question.objects.create(
                    survey=survey,
                    text=q["text"],
                    question_type=is_required,
                )
                for opt in q["options"]:
                    AnswerOption.objects.create(question=question, text=opt)

            return JsonResponse({"message": "Опрос успешно создан!"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Неверный формат данных"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET", "POST"])
def edit_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    if request.method == "GET":
        return render(request, "main/edit_survey.html", {"survey": survey})

    if request.content_type != "application/json":
        return JsonResponse({"error": "Unsupported content type"}, status=415)

    try:
        data = json.loads(request.body)
        title = data.get("title")
        description = data.get("description", "")
        questions_data = data.get("questions", [])

        if not title:
            return JsonResponse({"error": "Название обязательно"}, status=400)

        survey.title = title
        survey.description = description
        survey.save()

        existing_questions = {q.id: q for q in survey.question_set.all()}
        updated_question_ids = []

        for q_data in questions_data:
            q_id = q_data.get("id")
            q_text = q_data.get("text")
            q_type = q_data.get("type", "single_choice")
            q_required = q_data.get("required", True)
            q_options = q_data.get("options", [])

            if not q_text:
                continue

            if q_id and int(q_id) in existing_questions:
                question = existing_questions[int(q_id)]
                question.text = q_text
                question.question_type = q_type
                question.is_required = q_required
                question.save()
            else:
                question = Question.objects.create(
                    survey=survey,
                    text=q_text,
                    question_type=q_type,
                    is_required=q_required
                )

            updated_question_ids.append(question.id)

            # Обновляем варианты ответов
            existing_options = {opt.id: opt for opt in question.answeroption_set.all()}
            updated_option_ids = []

            for opt_text in q_options:
                if isinstance(opt_text, dict):
                    opt_id = opt_text.get("id")
                    text = opt_text.get("text", "").strip()
                else:
                    opt_id = None
                    text = str(opt_text).strip()

                if not text:
                    continue

                if opt_id and int(opt_id) in existing_options:
                    option = existing_options[int(opt_id)]
                    option.text = text
                    option.save()
                else:
                    option = AnswerOption.objects.create(question=question, text=text)

                updated_option_ids.append(option.id)

            # Удалим старые опции
            for opt in question.answeroption_set.all():
                if opt.id not in updated_option_ids:
                    opt.delete()

        # Удалим удалённые вопросы
        for q in survey.question_set.all():
            if q.id not in updated_question_ids:
                q.delete()

        return JsonResponse({"message": "Опрос успешно обновлён!"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Неверный формат данных"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def delete_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    if request.method == 'POST':
        survey.delete()
        return redirect('index')
    return render(request, 'main/confirm_delete.html', {'survey': survey})


def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            question.text = text
            question.save()
            return redirect('index')
    return render(request, 'main/edit_question.html', {'question': question})


def edit_answer_option(request, option_id):
    option = get_object_or_404(AnswerOption, id=option_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            option.text = text
            option.save()
            return redirect('index')
    return render(request, 'main/edit_answer_option.html', {'option': option})

def is_admin(user):
    return user.groups.filter(name='Администратор').exists()

def is_leader_or_admin(user):
    return user.groups.filter(name__in=['Администратор', 'Ведущий']).exists()



@login_required
@user_passes_test(is_admin)
def create_profile(request):
    if request.method == 'POST':
        tg_id = request.POST.get('tg_id')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        age = request.POST.get('age')

        if not tg_id:
            return render(request, 'main/create_profile.html', {'error': 'TG ID обязателен'})

        respondent, created = Respondent.objects.get_or_create(
            tgId=tg_id,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "age": age or None,
                "is_allowed": True
            }
        )
        if not created:
            return render(request, 'main/create_profile.html', {'error': 'Такой пользователь уже существует'})

        return redirect('index')

    return render(request, 'main/create_profile.html')




@login_required
def survey_stats(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    questions = survey.question_set.prefetch_related('answeroption_set')

    stats = []
    for question in questions:
        if question.question_type == 'text':
            # Текстовые ответы
            answers = Response.objects.filter(question=question).values_list('text_answer', flat=True)
            stats.append({
                'question': question,
                'type': 'text',
                'answers': list(answers)
            })
        else:
            # Выбор вариантов ответа
            options = question.answeroption_set.all()
            data = []
            for option in options:
                count = Response.objects.filter(question=question, selected_options=option).count()
                data.append((option.text, count))
            stats.append({
                'question': question,
                'type': 'choice',
                'data': data
            })

    return render(request, 'main/survey_stats.html', {
        'survey': survey,
        'stats': stats
    })

@csrf_exempt
def api_get_survey_unified(request):
    key = request.headers.get('X-API-KEY') or request.GET.get('api_key')
    if key != settings.API_SECRET_KEY:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Получаем параметры из GET или JSON-тела
    survey_id = request.GET.get('id')
    title = request.GET.get('title')

    if request.content_type == "application/json":
        try:
            body = json.loads(request.body)
            survey_id = body.get('id', survey_id)
            title = body.get('title', title)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not survey_id and not title:
        return JsonResponse({'error': 'Provide either "id" or "title"'}, status=400)

    try:
        if survey_id:
            survey = Survey.objects.get(id=survey_id)
        else:
            survey = Survey.objects.get(title=title)

        questions = []
        for question in survey.question_set.all():
            q_data = {
                'id': question.id,
                'text': question.text,
                'type': question.question_type,
                'required': question.is_required,
                'options': []
            }

            if question.question_type in ['single_choice', 'multiple_choice']:
                q_data['options'] = [
                    {'id': opt.id, 'text': opt.text}
                    for opt in question.answeroption_set.all()
                ]

            questions.append(q_data)

        return JsonResponse({
            'id': survey.id,
            'title': survey.title,
            'description': survey.description,
            'questions': questions
        }, status=200)

    except Survey.DoesNotExist:
        return JsonResponse({'error': 'Survey not found'}, status=404)

from django.conf import settings

@csrf_exempt
@require_POST
def receive_bot_answer(request):
    # Проверка API-ключа
    api_key = request.headers.get("X-API-KEY") or request.GET.get("api_key")
    if api_key != settings.API_SECRET_KEY:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        data = json.loads(request.body)

        user = data.get("user_info", {})
        question_text = data.get("question")
        answer_text = data.get("answer")

        if not user or not question_text or not answer_text:
            return JsonResponse({"error": "Недостаточно данных"}, status=400)

        # Найти или создать пользователя
        respondent, _ = Respondent.objects.get_or_create(
            tgId=user.get("user_id"),
            defaults={
                "first_name": user.get("full_name").split()[0] if user.get("full_name") else "",
                "last_name": user.get("full_name").split()[1] if user.get("full_name") and len(user.get("full_name").split()) > 1 else "",
            }
        )

        # Найти вопрос
        try:
            question = Question.objects.get(text=question_text)
        except Question.DoesNotExist:
            return JsonResponse({"error": "Вопрос не найден"}, status=404)

        # Найти или создать сессию
        session, _ = ResponseSession.objects.get_or_create(
            survey=question.survey,
            respondent=respondent,
        )

        # Сохранить ответ
        Response.objects.create(
            session=session,
            question=question,
            text_answer=answer_text,
        )

        return JsonResponse({"status": "ok"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Неверный JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def login_telegram(request):
    data = json.loads(request.body)
    tg_id = data.get("user_id")

    respondent, created = Respondent.objects.get_or_create(
        tgId=tg_id,
        defaults={
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", "")
        }
    )

    if not respondent.is_allowed:
        return JsonResponse({"error": "Доступ запрещён. Обратитесь к администратору."}, status=403)

    return JsonResponse({"status": "ok"})