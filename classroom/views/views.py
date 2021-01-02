from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils import timezone

from classroom import util
from classroom.models import Student, TeambuildingQuestion, SiteConfig, ExitTicket, homerooms


def index(request):
    if not util.check_active_student(request): return redirect("student_login")

    return render(request, "classroom/index.html", {
        "student": Student.objects.get(id=request.session['sid']),
        "questions": TeambuildingQuestion.objects.filter(active=True)
                     .exclude(response__student__id=request.session['sid'])
                     if SiteConfig.objects.get(key="answer_questions") else False,
        "exit_ticket": SiteConfig.objects.get(key="exit_ticket")
                       and not ExitTicket.objects.filter(student__id=request.session['sid'], date=timezone.now())
    })


def student_login(request):
    try:
        allowed = bool(SiteConfig.objects.get(key="student_login"))
    except:
        SiteConfig.init()
        return redirect('index')

    if request.method == "GET":
        return render(request, "classroom/student_login.html", {
            "login_allowed": allowed
        })
    else:
        data = request.POST
        sid = data['sid']

        if Student.objects.filter(id=sid, enabled=True).exists():
            request.session['sid'] = sid

        return redirect("index")


def admin(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponseForbidden()

    SiteConfig.init()

    return render(request, "classroom/admin.html", {
        "questions": TeambuildingQuestion.objects.all(),
        "config": SiteConfig.objects.all(),
        "homerooms": homerooms,
    })
