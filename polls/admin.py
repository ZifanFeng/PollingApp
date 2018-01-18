from django.contrib import admin
from .models import Question, Choices, Comment

# admin.site.register(Question)
# Register your models here.

class ChoiceInline(admin.TabularInline):
	model = Choices
	extra = 3
class QuestionAdmin(admin.ModelAdmin):
	fieldsets = [
	(None, 	{'fields':['pub_date']}),
	('Text info', {'fields':['question_text']}),
	]
	inlines = [ChoiceInline]
	list_display = ('__str__', 'colored_question', 'was_published_recently')
	list_filter = ['question_text']
	search_fields = ['question_text']

admin.site.register(Question, QuestionAdmin)

class CommentAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'question', 'created', 'active')
	list_filter = ('active', 'created', 'updated')
	search_fields = ('name', 'email', 'body')
admin.site.register(Comment, CommentAdmin)