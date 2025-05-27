import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import Survey, Question, AnswerOption, Response,Respondent,ResponseSession
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.views.decorators.http import require_POST
import logging
@login_required
def index(request):
    surveys = Survey.objects.all().order_by('-created_at')
    return render(request, 'main/index.html', {'surveys': surveys})

@csrf_exempt
@login_required
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

@login_required
@csrf_exempt
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

@login_required
def delete_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    if request.method == 'POST':
        survey.delete()
        return redirect('index')
    return render(request, 'main/confirm_delete.html', {'survey': survey})

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            question.text = text
            question.save()
            return redirect('index')
    return render(request, 'main/edit_question.html', {'question': question})

@login_required
def edit_answer_option(request, option_id):
    option = get_object_or_404(AnswerOption, id=option_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            option.text = text
            option.save()
            return redirect('index')
    return render(request, 'main/edit_answer_option.html', {'option': option})



@login_required
def survey_stats(request, survey_id):
    try:
        survey = Survey.objects.get(id=survey_id)
    except Survey.DoesNotExist:
        return render(request, 'error.html', {'message': 'Опрос не найден'})

    questions = survey.question_set.all()

    stats = []
    for question in questions:
        question_stats = {
            'question': question.text,
            'data': []
        }

        # Для вопросов с вариантами (single_choice, multiple_choice)
        if question.question_type in ['single_choice', 'multiple_choice']:
            options = question.answeroption_set.all()

            # Подсчитываем количество ответов для каждого варианта
            for option in options:
                count = Response.objects.filter(question=question, selected_options=option).count()
                question_stats['data'].append({
                    'option': option.text,
                    'count': count
                })

        stats.append(question_stats)

    return render(request, 'main/survey_stats.html', {'survey': survey, 'stats': stats})




@login_required
def create_profile(request):
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not username or not password:
            return render(request, 'main/create_profile.html', {'error': 'Логин и пароль обязательны'})

        hashed_password = make_password(password)

        user = User.objects.create(
            username=username,
            password=hashed_password,
        )


        if role == 'admin':
            # Если роль "admin", добавляем в группу "Администратор"
            admin_group = Group.objects.get(name='Администратор')
            user.groups.add(admin_group)
            user.is_superuser = True
            user.is_staff = True
        elif role == 'host':

            host_group = Group.objects.get(name='Ведущий')
            user.groups.add(host_group)

        # Сохраняем пользователя
        user.save()

        # Перенаправляем на главную страницу
        return redirect('index')

    # В случае метода GET, просто отрисовываем форму
    return render(request, 'main/create_profile.html')




STATIC_PASSWORD = '123'


def create_superuser(request):
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')

        admin_group, created = Group.objects.get_or_create(name='Администратор')

        user.groups.add(admin_group)


        user.save()

        return render(request, 'main/create_superuser_success.html')
    else:
        return render(request, 'main/create_superuser_exists.html')

@csrf_exempt
def api_get_survey(request):
    survey_id = request.GET.get('id')  # Получаем ID опроса из строки запроса
    if not survey_id:
        return JsonResponse({'error': 'Survey ID is required'}, status=400)

    try:
        survey = Survey.objects.get(id=survey_id)
        questions = []
        for question in survey.question_set.all():
            question_data = {
                'id': question.id,  # Передаем ID вопроса
                'text': question.text,
                'type': question.question_type,
                'required': question.is_required,
                'options': [{'id': option.id, 'text': option.text} for option in question.answeroption_set.all()]
            }
            questions.append(question_data)

        return JsonResponse({
            'id': survey.id,
            'title': survey.title,
            'description': survey.description,
            'questions': questions
        })
    except Survey.DoesNotExist:
        return JsonResponse({'error': 'Survey not found'}, status=404)

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def receive_bot_answer(request):
    try:

        logger.info(f"Received data: {request.body}")


        data = json.loads(request.body)

        user_info = data.get("user_info", {})
        answers = data.get("answers", [])


        if not user_info or not answers:
            logger.error("Недостаточно данных в запросе.")
            return JsonResponse({"error": "Недостаточно данных"}, status=400)


        logger.info(f"User info: {user_info}")


        respondent, created = Respondent.objects.get_or_create(
            tgId=user_info.get("user_id"),
            defaults={
                "first_name": user_info.get("full_name", "").split()[0] if user_info.get("full_name") else "",
                "last_name": user_info.get("full_name", "").split()[1] if user_info.get("full_name") and len(user_info.get("full_name").split()) > 1 else "",
            }
        )


        if created:
            logger.info(f"Created new respondent: {respondent}")
        else:
            logger.info(f"Found existing respondent: {respondent}")

        for answer in answers:
            question_id = answer.get("question_id")
            answer_text = answer.get("answer")

            if not question_id or not answer_text:
                logger.error(f"Некорректные данные: question_id: {question_id}, answer: {answer_text}")
                continue


            logger.info(f"Question ID: {question_id}, Answer: {answer_text}")


            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                logger.error(f"Question with ID {question_id} not found.")
                continue


            session, _ = ResponseSession.objects.get_or_create(
                survey=question.survey,
                respondent=respondent,
            )


            logger.info(f"Session created: {session}")


            response = Response.objects.create(
                session=session,
                question=question,
                text_answer=answer_text,
            )


            logger.info(f"Response saved: {response}")

        return JsonResponse({"status": "ok"})

    except json.JSONDecodeError:
        logger.error("Ошибка декодирования JSON.")
        return JsonResponse({"error": "Неверный JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)