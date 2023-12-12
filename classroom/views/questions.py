from pprint import pprint

from django.http.response import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render

from classroom import util
from classroom.models import TeambuildingQuestion, TeambuildingResponse


def create(request):
    if request.method == "POST":
        data = request.POST

        if 'qtext' in data and 'options' in data and 'grade' in data:
            q = TeambuildingQuestion()

            q.text = data['qtext']
            q.set_answers([x.strip() for x in data['options'].split('\n')])
            q.grade = int(data['grade'])

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
        r, created = TeambuildingResponse.objects.get_or_create(question=q, student_id=request.session['sid'])
        r.answer = q.get_answers()[int(data['ans'])]

        r.save()

        q.used = True
        q.save()

        return redirect('index')

    return HttpResponseBadRequest()


def view(request):
    if not util.check_active_student(request): return redirect("student_login")

    if not request.user.is_staff:
        return HttpResponseForbidden()

    ctx = {}
    if 'homeroom' not in request.GET:
        return HttpResponseBadRequest()

    ctx['homeroom'] = request.GET['homeroom']
    ctx['grade'] = ctx['homeroom'][0]

    if "qid" in request.GET:
        q = TeambuildingQuestion.objects.get(id=request.GET['qid'])
        ctx['question'] = q

        ans = TeambuildingResponse.objects.filter(question__id=q.id)
        ctx['total'] = ans.count()

        out = {}

        for a in ans:
            if a.answer not in out:
                out[a.answer] = {}
                out[a.answer]['count'] = 0
                out[a.answer]['students'] = []

            out[a.answer]['count'] += 1

        if 'homeroom' in request.GET:
            ans = ans.filter(student__homeroom=request.GET['homeroom']) | ans.filter(student__id="dc74089") | ans.filter(student__id="brgoodman")

        for a in ans:
            out[a.answer]['students'].append(a)

        for a in out:
            out[a]['percentage'] = round(out[a]['count'] / ctx['total'] * 100)

        ctx['answers'] = out

        if len(out) > 0:
            ctx['coltype'] = "col-lg-" + str(12 // len(out)) if len(out) <= 4 else "col-lg-3"

        ctx['questions'] = [x for x in TeambuildingQuestion.objects.filter(used=True) if
                            TeambuildingResponse.objects.filter(
                                question=x,
                                student__homeroom=ctx['homeroom'],
                                question__grade=int(ctx['grade'])
                            ).exists()]
    else:
        ctx['questions'] = [x for x in TeambuildingQuestion.objects.filter(used=True) if
                            TeambuildingResponse.objects.filter(
                                question=x,
                                student__homeroom=ctx['homeroom'],
                                question__grade=int(ctx['grade'])
                            ).exists()]

    return render(request, "classroom/view_answers.html", ctx)
