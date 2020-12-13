from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect

from classroom.models import TeambuildingQuestion, TeambuildingResponse


def create(request):
    if request.method == "POST":
        data = request.POST

        if 'qtext' in data and 'options' in data:
            q = TeambuildingQuestion()

            q.text = data['qtext']
            q.set_answers([x.strip() for x in data['options'].split('\n')])

            q.save()

            return redirect('admin')
    return HttpResponseBadRequest()


def select(request):
    for q in TeambuildingQuestion.objects.all():
        q.used = TeambuildingResponse.objects.filter(question__id=q.id).exists()
        q.active = False
        q.save()

    if request.method == "POST" and 'questions' in request.POST:
        for qid in request.POST.getlist("questions"):
            q = TeambuildingQuestion.objects.get(id=qid)
            q.active = True
            q.save()

    return redirect('admin')
