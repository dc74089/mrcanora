from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect

from classroom import util
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


def answer(request):
    if not util.check_active_student(request): return redirect("student_login")

    if request.method == "GET" and all([x in request.GET for x in ("qid", "ans")]):
        data = request.GET

        q = TeambuildingQuestion.objects.get(id=data['qid'])
        r = TeambuildingResponse(question=q, student_id=request.session['sid'])
        r.answer = q.get_answers()[int(data['ans'])]

        r.save()

        return redirect('index')

    return HttpResponseBadRequest()
