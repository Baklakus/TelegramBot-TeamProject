from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Survey, Question, AnswerOption, Respondent, ResponseSession, Response
# Register your models here.

Group.objects.get_or_create(name='Администратор')
Group.objects.get_or_create(name='Ведущий')

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 1


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    inlines = [AnswerOptionInline]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey', 'question_type', 'is_required')
    list_filter = ('question_type', 'survey')


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question')


@admin.register(Respondent)
class RespondentAdmin(admin.ModelAdmin):
    list_display = ('tgId', 'first_name', 'last_name', 'age', 'registration_date')
    search_fields = ('first_name', 'last_name', 'tgId')


@admin.register(ResponseSession)
class ResponseSessionAdmin(admin.ModelAdmin):
    list_display = ('survey', 'respondent', 'started_at')


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('question', 'session', 'created_at')
    list_filter = ('question__survey',)