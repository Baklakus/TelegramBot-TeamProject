from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),  # Главная страница

    # Опросы
    path('create_survey/', views.create_survey, name='create_survey'),
    path('survey/<int:survey_id>/edit/', views.edit_survey, name='edit_survey'),
    path('survey/<int:survey_id>/delete/', views.delete_survey, name='delete_survey'),
    path('survey/<int:survey_id>/stats/', views.survey_stats, name='survey_stats'),

    # Вопросы и варианты ответов
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('answer_option/<int:option_id>/edit/', views.edit_answer_option, name='edit_answer_option'),

    # Авторизация
    path('login/', auth_views.LoginView.as_view(template_name='main/user_login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Создание профиля
    path('create_profile/', views.create_profile, name='create_profile'),

    #API
    #path('receive_bot_answer/', views.receive_bot_answer, name='receive_bot_answer'),
    path('api/survey/', views.api_get_survey, name='api_get_survey_unified'),
    path('api/answers/', views.receive_bot_answer, name='receive_bot_answer'),
    path('create-superuser/', views.create_superuser, name='create_superuser'),
]
