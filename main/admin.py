from django.contrib import admin
from django.db.models import Count
from .models import Survey, Question, AnswerOption, Respondent, ResponseSession, Response


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 1
    readonly_fields = ['text', 'get_response_count']

    def get_response_count(self, obj):
        # Подсчитываем количество ответов для этой опции
        return Response.objects.filter(selected_options=obj).count()
    get_response_count.short_description = 'Количество ответов'


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    inlines = [AnswerOptionInline]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'get_question_count', 'get_answer_count')
    search_fields = ('title',)
    inlines = [QuestionInline]

    def get_question_count(self, obj):
        # Подсчитываем количество вопросов для данного опроса
        return obj.question_set.count()
    get_question_count.short_description = 'Количество вопросов'

    def get_answer_count(self, obj):
        # Подсчитываем общее количество ответов для этого опроса
        return Response.objects.filter(question__survey=obj).count()
    get_answer_count.short_description = 'Количество ответов'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey', 'question_type', 'is_required', 'get_answer_count', 'get_option_count')
    list_filter = ('question_type', 'survey')
    inlines = [AnswerOptionInline]

    def get_answer_count(self, obj):
        # Подсчитываем количество ответов для данного вопроса
        return Response.objects.filter(question=obj).count()
    get_answer_count.short_description = 'Количество ответов'

    def get_option_count(self, obj):
        # Подсчитываем количество вариантов для этого вопроса
        return obj.answeroption_set.count()
    get_option_count.short_description = 'Количество вариантов'


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'get_response_count')

    def get_response_count(self, obj):
        # Подсчитываем количество ответов для этого варианта
        return Response.objects.filter(selected_options=obj).count()
    get_response_count.short_description = 'Количество ответов'


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
