from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from classroom import util
from classroom.models import Student, TeambuildingQuestion, SiteConfig


def index(request):
    if not util.check_active_student(request): return redirect("student_login")

    return render(request, "classroom/index.html", {
        "student": Student.objects.get(id=request.session['sid'])
    })


def student_login(request):
    if not SiteConfig.objects.get(key="student_login"):
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, "classroom/student_login.html")
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
        "questions": TeambuildingQuestion.objects.filter(used=False) |
                     TeambuildingQuestion.objects.filter(active=True),
        "config": SiteConfig.objects.all()
    })
