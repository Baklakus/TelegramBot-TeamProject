from django import forms
from .models import Survey, Question, AnswerOption

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['survey', 'text', 'question_type', 'is_required']

class AnswerOptionForm(forms.ModelForm):
    class Meta:
        model = AnswerOption
        fields = ['text']