from django import forms
from django.forms import modelformset_factory

from .models import Question, Choices, Comment
class ChoiceForm(forms.ModelForm):
	choice_text = forms.CharField(required=False)
	class Meta:
		model = Choices
		fields = ('choice_text',)

ChoiceFormSet = modelformset_factory(Choices, form=ChoiceForm)

class QuestionForm(forms.ModelForm):
	class Meta:
		 model = Question
		 formset = ChoiceFormSet(queryset=Choices.objects.all())
		 fields = ('question_text', )

class EmailPostForm(forms.Form):
	name = forms.CharField(max_length=25)
	email = forms.EmailField()
	to = forms.EmailField()
	comments = forms.CharField(required=False, widget = forms.Textarea)

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ('name', 'email', 'body')
		
	# question_text = forms.CharField(max_length = 200)
	# #choices_setssss = forms.ModelMultipleChoiceField(queryset = Choices.objects.all())
	# ChoiceFormSet = formset_factory(ChoiceForm, extra = 3)
	# formset = ChoiceFormSet()
	# for form in formset:
	# 	print(form.as_table())