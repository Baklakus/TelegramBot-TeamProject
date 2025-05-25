from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # теперь главная страница — index.html
    path('create_survey/', views.create_survey, name='create_survey'),
    path('survey/<int:survey_id>/edit/', views.edit_survey, name='edit_survey'),
    path('survey/<int:survey_id>/delete/', views.delete_survey, name='delete_survey'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('answer_option/<int:option_id>/edit/', views.edit_answer_option, name='edit_answer_option'),
    path('login/', auth_views.LoginView.as_view(template_name='main/user_login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('create_profile/', views.create_profile, name='create_profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('survey/<int:survey_id>/stats/', views.survey_stats, name='survey_stats'),
    path('api/survey/', views.api_get_survey_unified, name='api_get_survey_unified'),
    path('api/login_telegram/', views.login_telegram, name='login_telegram'),
]