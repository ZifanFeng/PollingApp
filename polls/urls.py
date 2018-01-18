from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.views.decorators.http import require_POST
from .feeds import LatestPollsFeed

app_name = 'polls'
urlpatterns = [path("", views.IndexView.as_view(), name="index"),
				path("<int:pk>/", views.DetailView.as_view(), name='detail'),
				path('<int:pk>/results/', views.ResultsView.as_view(), name="results"),
				path('<int:question_id>/vote/', views.vote, name='vote'),
				path("new/", views.question_new, name="question_new"),
				path("<int:pk>/edit/", views.question_edit, name="question_edit"),
				path("<int:question_id>/share", views.post_share, name="post_share"),
				path("commentform/", require_POST(views.CommentFormView.as_view()), name="commentform"),
				path("feed/", LatestPollsFeed(), name="polls_feed"),
				
				]

