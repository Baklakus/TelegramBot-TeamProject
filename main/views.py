import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import update_session_auth_hash
import logging
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.db.models import Count



@login_required
def index(request):
    surveys = Survey.objects.all().order_by('-created_at')
    return render(request, 'main/index.html', {'surveys': surveys})

def is_admin(user):
    return user.groups.filter(name='Administrator').exists()

@login_required
def create_survey(request):
    if request.method == 'GET':
        # Возвращаем страницу для создания опроса
        return render(request, 'main/create_survey.html')

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get("title")
            description = data.get("description", "")
            questions = data.get("questions", [])

            if not title:
                return JsonResponse({"error": "Название опроса обязательно"}, status=400)

            # Создание опроса
            survey = Survey.objects.create(title=title, description=description)
            for q in questions:
                is_required = q.get("required", False)
                question = Question.objects.create(
                    survey=survey,
                    text=q["text"],
                    question_type=q["type"],
                    is_required=is_required,
                )
                for opt in q["options"]:
                    is_correct = opt.get('is_correct', False)  # Проверка на правильность
                    AnswerOption.objects.create(
                        question=question,
                        text=opt['text'],
                        is_correct=is_correct
                    )

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
                    is_correct = opt_text.get("is_correct", False)  # Сохраняем правильность
                else:
                    opt_id = None
                    text = str(opt_text).strip()
                    is_correct = False  # По умолчанию вариант не правильный

                if not text:
                    continue

                if opt_id and int(opt_id) in existing_options:
                    option = existing_options[int(opt_id)]
                    option.text = text
                    option.is_correct = is_correct
                    option.save()
                else:
                    option = AnswerOption.objects.create(question=question, text=text, is_correct=is_correct)

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
@csrf_exempt
def delete_question(request, survey_id):  # Убедитесь, что параметр survey_id передается в функцию
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question_id = data.get('question_id')

            # Получаем опрос и вопрос по ID
            survey = get_object_or_404(Survey, id=survey_id)
            question = get_object_or_404(Question, id=question_id, survey=survey)

            # Удаляем вопрос
            question.delete()

            return JsonResponse({"message": "Вопрос успешно удалён!"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Неверный метод запроса"}, status=400)


from django.db.models import Count


@login_required
def option_statistics(request, survey_id=None, question_id=None):
    """
    Подсчитывает количество выборов для вариантов ответа
    Возможна фильтрация по опросу и/или вопросу
    """
    # Базовый запрос для вариантов ответа
    options = AnswerOption.objects.annotate(
        num_responses=Count('response')  # Считаем связанные ответы
    ).select_related('question', 'question__survey')

    # Фильтрация по опросу если указан survey_id
    if survey_id:
        options = options.filter(question__survey_id=survey_id)

    # Фильтрация по вопросу если указан question_id
    if question_id:
        options = options.filter(question_id=question_id)

    # Группируем результаты
    stats = []
    for option in options:
        stats.append({
            'option_id': option.id,
            'option_text': option.text,
            'question_id': option.question.id,
            'question_text': option.question.text,
            'survey_id': option.question.survey.id,
            'survey_title': option.question.survey.title,
            'num_responses': option.num_responses,
        })

    return JsonResponse({'stats': stats})


@login_required
def survey_stats(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    # Получаем статистику через новую функцию
    stats_response = option_statistics(request, survey_id=survey_id)
    stats_data = json.loads(stats_response.content)['stats']

    # Группируем по вопросам
    question_stats = {}
    for item in stats_data:
        qid = item['question_id']
        if qid not in question_stats:
            question_stats[qid] = {
                'question': item['question_text'],
                'data': []
            }
        question_stats[qid]['data'].append({
            'option': item['option_text'],
            'count': item['num_responses']
        })

    return render(request, 'main/survey_stats.html', {
        'survey': survey,
        'question_stats': list(question_stats.values())
    })


@login_required
def user_activity(request):
    # Получаем всех респондентов
    respondents = Respondent.objects.all()

    activity_data = []
    for respondent in respondents:
        # Получаем сессии ответов для респондента
        sessions = ResponseSession.objects.filter(respondent=respondent).order_by('-started_at')

        last_activity_time = 'Нет данных'
        total_responses = 0
        surveys = []

        for session in sessions:
            # Добавляем информацию о сессии, опросе и времени
            survey_title = session.survey.title
            survey_date = session.started_at
            total_responses += Response.objects.filter(session=session).count()  # Количество ответов

            responses = []
            for response in Response.objects.filter(session=session):
                # Получаем варианты, которые выбрал респондент
                selected_options = response.selected_options.all()
                options_text = [option.text for option in selected_options]

                responses.append({
                    'question_text': response.question.text,
                    'selected_options': ', '.join(options_text),  # Список выбранных вариантов
                })

            surveys.append({
                'survey_title': survey_title,
                'survey_date': survey_date,
                'total_responses': total_responses,
                'responses': responses,
            })

            # Последняя активность
            last_activity_time = survey_date

        activity_data.append({
            'respondent': respondent,
            'last_activity_time': last_activity_time,
            'surveys': surveys
        })

    return render(request, 'main/user_activity.html', {'activity_data': activity_data})




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


from django.contrib.auth.models import User, Group
from django.shortcuts import render

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
        # Парсим входящий JSON
        data = json.loads(request.body)
        user_info = data.get("user_info", {})
        answers = data.get("answers", [])

        # Проверка обязательных полей
        if not user_info or not answers:
            return JsonResponse({"error": "Missing required data"}, status=400)

        # Получаем или создаем респондента
        respondent, created = Respondent.objects.get_or_create(
            tgId=user_info["user_id"],
            defaults={
                "first_name": user_info.get("full_name", "").split()[0],
                "last_name": " ".join(user_info.get("full_name", "").split()[1:])[:100],
            }
        )

        # Обрабатываем каждый ответ
        for answer in answers:
            question_id = answer.get("question_id")
            answer_text = answer.get("answer", "")

            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                continue  # Пропускаем несуществующие вопросы

            # Получаем или создаем сессию опроса
            session, _ = ResponseSession.objects.get_or_create(
                survey=question.survey,
                respondent=respondent,
            )

            # Создаем ответ и связываем с вариантами если нужно
            response = Response.objects.create(
                session=session,
                question=question,
                text_answer=answer_text,
            )

            # Для вопросов с выбором находим соответствующий вариант
            if question.question_type != 'text':
                try:
                    option = AnswerOption.objects.get(
                        question=question,
                        text=answer_text
                    )
                    response.selected_options.add(option)
                except AnswerOption.DoesNotExist:
                    pass

        return JsonResponse({"status": "success"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



@login_required
def profile_list(request):
    users = User.objects.all()  # Получаем всех пользователей
    return render(request, 'main/profile_list.html', {'users': users})


@login_required
def edit_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Обработка данных пользователя
        user_form = UserChangeForm(request.POST, instance=user)

        # Если форма для данных пользователя прошла валидацию, обновляем данные
        if user_form.is_valid():
            user_form.save()

        # Обработка изменения пароля
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if new_password1 and new_password1 == new_password2:
            user.set_password(new_password1)  # Устанавливаем новый пароль
            user.save()

        # Сохраняем сессию после изменения пароля
        update_session_auth_hash(request, user)

        return redirect('profile_list')  # Перенаправление на список профилей
    else:
        user_form = UserChangeForm(instance=user)

    return render(request, 'main/edit_profile.html', {'user_form': user_form, 'user': user})

@login_required
def delete_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('profile_list')  # Перенаправление после удаления
    return render(request, 'main/delete_profile.html', {'user': user})

