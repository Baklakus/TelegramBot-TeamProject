from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    path('create_superuser/', views.create_superuser, name='create_superuser'),
    # Опросы
    path('create_survey/', views.create_survey, name='create_survey'),
    path('survey/<int:survey_id>/edit/', views.edit_survey, name='edit_survey'),
    path('survey/<int:survey_id>/delete/', views.delete_survey, name='delete_survey'),
    path('survey/<int:survey_id>/stats/', views.survey_stats, name='survey_stats'),
    path('survey/<int:survey_id>/delete_question/', views.delete_question, name='delete_question'),

    # Вопросы и варианты ответов
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('answer_option/<int:option_id>/edit/', views.edit_answer_option, name='edit_answer_option'),

    # Авторизация
    path('login/', auth_views.LoginView.as_view(template_name='main/user_login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Создание профиля
    path('create_profile/', views.create_profile, name='create_profile'),

    # Страница с перечнем пользователей (управление профилями)
    path('profiles/', views.profile_list, name='profile_list'),

    # Редактирование профиля
    path('profiles/edit/<int:user_id>/', views.edit_profile, name='edit_profile'),

    # Удаление профиля
    path('profiles/delete/<int:user_id>/', views.delete_profile, name='delete_profile'),

    path('user_activity/', views.user_activity, name='user_activity'),
]
