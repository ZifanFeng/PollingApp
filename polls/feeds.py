from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Question
from django.utils import timezone


class LatestPollsFeed(Feed):
	title="All questions"
	link = "/polls/"
	description = 'New questions'

	def items(self):
		return Question.objects.filter(pub_date__lte=timezone.now())[:5]

	def item_title(self, item):
		return item.question_text

	def item_description(self, item):
		return truncatewords(item.question_text, 30)


