from django.db import models
import datetime
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

from django.utils.html import format_html
from django.contrib.auth.models import User
from django.urls import reverse
# from taggit.managers import TaggableManager

# Create your models here.


class Question(models.Model):
	question_text = models.CharField(max_length = 200)
	pub_date = models.DateTimeField("Published date")
	# tags = TaggableManager( on_delete=models.CASCADE)
	def __str__(self):
		return self.question_text

	def was_published_recently(self):
		now = timezone.now()
		return now - datetime.timedelta(days=1) <= self.pub_date  <= now
	was_published_recently.admin_order_field = 'pub_date'
	was_published_recently.boolean = True
	was_published_recently.short_description = "Published in one day?"

	def colored_question(self):
		return format_html(
			'<span style="color: #aa0;">{}</span>',
			self.question_text,
		)
	colored_question.admin_order_field = '-question_text'

	def get_absolute_url(self):
		return reverse('polls:detail', args=[self.id])

class Choices(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices_set")
	choice_text = models.CharField(max_length = 100)
	votes = models.IntegerField(default = 0)

	def __str__(self):
		return self.choice_text

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
	favourite = models.ManyToManyField(Question)

	def __str__(self):
		return self.user.first_name

	@receiver(post_save, sender=settings.AUTH_USER_MODEL)
	def create_profile_for_new_user(sender, created, instance, **kwargs):
	    if created:
	        profile = Profile(user=instance)
	        profile.save()

class Comment(models.Model):
	question = models.ForeignKey(Question, related_name="comments", on_delete=models.CASCADE)
	name = models.CharField(max_length=80)
	email = models.EmailField()
	body = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now = True)
	active = models.BooleanField(default=True)
	class Meta:
		ordering = ("created", )
	def __str__(self):
		return 'Comment by {} on {}'.format(self.name, self.question)



