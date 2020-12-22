from django.http.response import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render

from classroom import util
from classroom.models import TeambuildingQuestion, TeambuildingResponse, SiteConfig


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

        q.used = True
        q.save()

        return redirect('index')

    return HttpResponseBadRequest()


def view(request):
    if not util.check_active_student(request): return redirect("student_login")

    if not SiteConfig.objects.get(key="view_answers") and not request.user.is_superuser:
        return HttpResponseForbidden()

    ctx = {}
    if 'homeroom' in request.GET:
        ctx['homeroom'] = request.GET['homeroom']

    if "qid" in request.GET:
        q = TeambuildingQuestion.objects.get(id=request.GET['qid'])
        ctx['question'] = q

        ans = TeambuildingResponse.objects.filter(question__id=q.id)
        out = {}

        if 'homeroom' in request.GET:
            ans = ans.filter(student__homeroom=request.GET['homeroom'])

        for a in ans:
            if a.answer not in out:
                out[a.answer] = []

            out[a.answer].append(a)

        ctx['answers'] = out
        if len(out) > 0:
            ctx['coltype'] = "col-lg-" + str(12//len(out)) if len(out) <= 4 else "col-4"

        ctx['questions'] = TeambuildingQuestion.objects.filter(used=True).exclude(id=q.id)
    else:
        ctx['questions'] = TeambuildingQuestion.objects.filter(used=True)

    return render(request, "classroom/view_answers.html", ctx)
