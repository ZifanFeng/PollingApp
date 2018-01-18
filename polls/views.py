from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from .models import Question, Choices
from django.utils import timezone
from django.utils.decorators import method_decorator
from .forms import QuestionForm, ChoiceForm, EmailPostForm, CommentForm
from django.forms.models import modelformset_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.views.generic.edit import FormMixin



# def UserViewVote(request):
# 	username = request.POST["username"]
# 	password = request.POST["password"]
# 	user = authenticate(request, username = username, password = password)
# 	if user is not None:
# 		login(request, user)
# 	else:

# def logoutView(request):
# 	logout(request)

def post_share(request, question_id):
	print("post_share")
	question = get_object_or_404(Question, id=question_id)
	sent = False
	if request.method=="POST":
		form = EmailPostForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			post_url = request.build_absolute_uri(question.get_absolute_url())
			subject = '{} ({}) ask you to fill out the "{}"'.format(cd['name'], cd["email"], question.question_text)
			message = 'As the title, check the link at {} \n \n '.format(post_url, cd['comments'])
			send_mail(subject, message, 'admin@myblog.com', [cd["to"]])
			sent = True
	else:
		form = EmailPostForm()
	return render(request, 'polls/share.html', {'question': question, 'form': form, 'sent':sent})

@method_decorator(login_required(login_url='/accounts/login/'), name="dispatch", )
class IndexView(generic.ListView):
	template_name = "polls/index.html"
	context_object_name = "latest_question_list"
	paginate_by = 3
	def get_queryset(self):
		return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

# def index(request):
# 	latest_q_list = Question.objects.order_by('-pub_date')[:5]
# 	template = loader.get_template('polls/index.html')
# 	context = {
# 		'latest_question_list' : latest_q_list
# 	}
# 	return render(request, 'polls/index.html', context)
	#return HttpResponse(template.render(context, request))
	
# Create your views here.
class DetailView(FormMixin, generic.DetailView):
	model = Question
	# favourite = models.BooleanField(default=False)
	template_name = "polls/detail.html"
	form_class = CommentForm

	def get_success_url(self):
		return reverse("polls:detail", kwargs={'pk': self.object.pk})
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = self.get_form()
		return context
	def post(self, request, pk):
		question = get_object_or_404(Question, pk=pk)
		if 'favourite' in request.POST and request.POST['favourite']:
			user = request.user
			profile = user.profile
			try:
				profile.favourite.add(question)
				profile.save()
			except (KeyError, Question.DoesNotExist):
				print("DNE")
			return render(request, self.template_name,{"question":question})
		self.object = self.get_object()
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, question)
		else:
			return self.form_invalid(form)
	def form_valid(self,form, question):
		new_comment = form.save(commit=False)
		new_comment.question = question
		new_comment.save()
		return super().form_valid(form)

	def get_queryset(self):
		return Question.objects.filter(pub_date__lte=timezone.now())
	# def get_context_data(self, **kwargs):
	# 	context = super(DetailView, self).get_context_data(**kwargs)
	# 	context['form'] = CommentFormView
	# 	return context

class CommentFormView(generic.FormView):
	form_class = CommentForm
	def form_valid(self, form):
		new_comment = form.save(commit=False)
		# new_comment.question = self.request.question
		new_comment.save()
		return super().form_valid(form)
	#try:
	#	question = Question.objects.get(pk=question_id)
	#except Question.DoesNotExist:
	#	raise Http404("Question DNE")

	# question = get_object_or_404(Question,pk=question_id)
	# return render(request, "polls/detail.html", {"question":question})
class ResultsView(generic.DetailView):
	model = Question
	template_name = "polls/results.html"
	def get_queryset(self):
		return Question.objects.filter(pub_date__lte=timezone.now())
	#t
# def results(request, question_id):
# 	question = get_object_or_404(Question, pk=question_id)
# 	return render(request, 'polls/results.html', {"question":question})
def vote(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = question.choices_set.get(pk=request.POST["choice"])
	except (KeyError, Choices.DoesNotExist):
		return render(request, "polls/detail.html", {
			"question":question, 
			"error_message":"You did not select a choice"
			})
	else:
		selected_choice.votes += 1
		selected_choice.save()

	return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def question_new(request):
	extra_form = 2
	RelatedFormset = modelformset_factory(Choices,  form=ChoiceForm, extra = 3, can_delete=True)
	formset = RelatedFormset(queryset=Choices.objects.none())
	if request.method=="POST":
		form = QuestionForm(request.POST)
		if 'addchoice' in request.POST and request.POST['addchoice']=='true':
			formset_dictionary_copy = request.POST.copy()
			formset_dictionary_copy["form-TOTAL_FORMS"] = int(formset_dictionary_copy["form-TOTAL_FORMS"])+extra_form
			formset = RelatedFormset(formset_dictionary_copy)
		elif form.is_valid():
			
			formset = RelatedFormset(request.POST)
			if form.is_valid() and formset.is_valid():
				question = form.save(commit = False)
				question.pub_date = timezone.now()
				question.save()
				for cform in formset:
					if cform.is_valid() and cform.has_changed() and 'choice_text' in cform.changed_data:
						choice = cform.save(commit=False)
						choice.question = question
						choice.save()
				for dform in formset.deleted_forms:
					c = dform.save(commit=False)
					c.delete()
				return redirect("polls:detail", pk = question.pk)
	else:
		form = QuestionForm()
	return render(request, 'polls/question_edit.html', {'form': form, 'formset':formset})

def question_edit(request, pk):
	question = get_object_or_404(Question, pk = pk)
	extra_form = 2
	RelatedFormset = modelformset_factory(Choices,  form=ChoiceForm, extra = 0, can_delete=True)
	formset = RelatedFormset(queryset=Choices.objects.none())
	if request.method=="POST":
		if 'addchoice' in request.POST and request.POST['addchoice']=='true':
			form = QuestionForm(request.POST, instance = question)
			formset_dictionary_copy = request.POST.copy()
			formset_dictionary_copy["form-TOTAL_FORMS"] = int(formset_dictionary_copy["form-TOTAL_FORMS"])+extra_form
			formset = RelatedFormset(formset_dictionary_copy)
			return render(request, 'polls/question_edit.html', {'form':form, "formset":formset})

		else:
			form = QuestionForm(request.POST, instance=question)
			formset = RelatedFormset(request.POST, queryset = question.choices_set.all())
			if form.is_valid() and formset.is_valid():
				question = form.save(commit=False)
				question.pub_date = timezone.now()
				for cform in formset:
					if cform.is_valid() and cform.has_changed() and 'choice_text' in cform.changed_data:
						choice = cform.save(commit=False)
						choice.question = question
						choice.save()
				for dform in formset.deleted_forms:
					c = dform.save(commit=False)
					c.delete()

				question.save()
				return redirect("polls:detail", pk=question.pk)
	else:
		form = QuestionForm(instance = question)
		formset = RelatedFormset(queryset=question.choices_set.all())

	return render(request, 'polls/question_edit.html', {'form':form, "formset":formset})







