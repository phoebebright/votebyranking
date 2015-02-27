from django.shortcuts import render
from web.models import *
# Create your views here.

from django.shortcuts import render_to_response,  HttpResponseRedirect
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic.base import View
from django.views.generic import TemplateView,ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.core.urlresolvers import reverse

from lazysignup.decorators import allow_lazy_user
from lazysignup.utils import is_lazy_user

#python
import json
import csv
from datetime import datetime,timedelta, date


class Ask(TemplateView):


    template_name = "ask.html"

    def get_context_data(self, **kwargs):
        context = super(Ask, self).get_context_data(**kwargs)
        context['question'] = Question.objects.get(id=1)
        context['answers'] = Answer.objects.filter(question_id=1).order_by('?')
        return context


@allow_lazy_user
def save_answers(request, question_id):

    me = request.user

    question = Question.objects.get(id=question_id)
    answers = Submission.objects.filter(question=question, user=me)

    if is_lazy_user(me):
        return  HttpResponseRedirect(reverse('lazysignup_convert'))



    return  HttpResponseRedirect(reverse('home'))





@allow_lazy_user
def update_order(request, question_id):

    if request.method == "POST":

        me = request.user

        question = Question.objects.get(id=question_id)
        answers = request.POST.get('answers').split("|")

        n = 0
        for id in answers:
            answer = Answer.objects.get(id=id)
            try:
                sub = Submission.objects.get(question=question, answer=answer, user=me)
                sub.score = n
                sub.save()
            except Submission.DoesNotExist:
                Submission.objects.create(question=question, answer=answer, user=me, score=n)


            n += 1


    return HttpResponse("OK")