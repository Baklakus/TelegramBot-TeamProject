from django.db import models


class Respondent(models.Model):
    tgId= models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Респондент"
        verbose_name_plural = "Респонденты"


class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"


class Question(models.Model):
    QUESTION_TYPES = (
        ('text', 'Текстовый ответ'),
        ('single_choice', 'Один вариант'),
        ('multiple_choice', 'Множественный выбор'),
    )

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"


class ResponseSession(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    respondent = models.ForeignKey(
        Respondent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сессия ответов"
        verbose_name_plural = "Сессии ответов"


class Response(models.Model):
    session = models.ForeignKey(ResponseSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    selected_options = models.ManyToManyField(AnswerOption, blank=True)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"