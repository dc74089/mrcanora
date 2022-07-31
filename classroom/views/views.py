from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils import timezone

from classroom import util
from classroom.models import Student, TeambuildingQuestion, SiteConfig, ExitTicket, homerooms, Assignment


def index(request):
    if not util.check_active_student(request): return redirect("student_login")

    # Transform assignments
    assignments = {}
    for a in Assignment.objects.all():
        if a.module not in assignments:
            assignments[a.module] = []

        assignments[a.module].append(a)

    s = Student.objects.get(id=request.session['sid'])
    etq = s.entryticket_set.filter(date__gte=timezone.now() - timezone.timedelta(hours=12))

    greeting = util.do_greeting(request, s)
    questions = util.do_questions(request, s)
    music = util.do_music(request, s)
    bdays = util.get_bdays() if request.user.is_authenticated else False

    return render(request, "classroom/index.html", util.smoosh(SiteConfig.all_configs(), {
        "student": s,
        "greeting": greeting,
        "questions": questions if SiteConfig.objects.get(key="answer_questions") else False,
        "assignments": assignments,
        "seat_options": util.seats,
        "entry_ticket": SiteConfig.objects.get(key="entry_ticket")
                        and not etq.exists(),
        "covid": SiteConfig.objects.get(key="covid")
                        and not etq.exists(),
        "exit_ticket": SiteConfig.objects.get(key="exit_ticket")
                       and not ExitTicket.objects.filter(student__id=request.session['sid'], date=timezone.now()),
        "music": music,
        "bdays": bdays
    }))


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
        "questions": TeambuildingQuestion.objects.all().order_by('grade'),
        "config": SiteConfig.objects.all().order_by("key"),
        "homerooms": homerooms,
    })
