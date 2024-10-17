from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
#from django.template import loader
from .models import Question, Choice
#from django.http import Http404
from django.db.models import F
from django.urls import reverse
from django.views import generic
from django.views.decorators.http import require_POST
from .forms import QuestionForm, ChoiceForm


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]

class IndexAdminView(generic.ListView):
    template_name = "polls/adminindex.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

class DetailViewUpdate(generic.DetailView):
    model = Question
    template_name = "polls/detailupdate.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def question_view(request):
    if request.method == "POST":
       form = QuestionForm(request.POST)
       if form.is_valid():
          form.save()
          return render(request, "polls/success.html")
    else:
        form = QuestionForm()
    return render(request, 'polls/question.html', {'form': form})

def choice_view(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            return HttpResponseRedirect(reverse("polls:detail", args=(question_id,)))
    else:
      
        form = ChoiceForm()

    
    return render(request, "polls/choice.html", {"form": form, "question": question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

@require_POST
def update(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.method == "POST":
        question.question_text = request.POST.get('question_text')
        question.pub_date = request.POST.get('question_date')

        # Obtener textos de opciones existentes
        choice_texts = [request.POST.get(f'choice_text{i}') for i in range(1, len(question.choice_set.all()) + 1)]
        new_choices = request.POST.getlist('new_choice')

        # Limpiar opciones existentes
        question.choice_set.all().delete()

        # Guardar opciones existentes
        for choice_text in choice_texts:
            if choice_text:
                Choice.objects.create(question=question, choice_text=choice_text)

        # Guardar nuevas opciones
        for new_choice in new_choices:
            if new_choice:
                Choice.objects.create(question=question, choice_text=new_choice)
        #falta actualizar fecha??
        question.save()
        return HttpResponseRedirect(reverse('polls:detailupdate', args=(question.id,)))

