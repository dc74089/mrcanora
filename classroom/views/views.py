import random

from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone

from classroom import util
from classroom.models import Student, TeambuildingQuestion, SiteConfig, ExitTicket, homerooms, EntryTicket, Assignment


def index(request):
    if not util.check_active_student(request): return redirect("student_login")

    # Transform assignments
    assignments = {}
    for a in Assignment.objects.all():
        if a.module not in assignments:
            assignments[a.module] = []

        assignments[a.module].append(a)

    seats = {
        # "Under the Hallway Window": ["Seat 1", "Seat 2", "Seat 3", "Seat 4", "Seat 5"],
        "Left of the TV": ["Seat 6", "Seat 7", "Seat 8", "Seat 9", "Seat 10", "Seat 11", "Seat 12"],
        "Under the Outside Window": ["Seat 13", "Seat 14", "Seat 15", "Seat 16"],
        "In a Movable Chair": ["Spot 17", "Spot 18", "Spot 19", "Spot 20", "Spot 21", "Spot 22", "Spot 23", "Spot 24",
                               "Spot 25"],
        "Under the TV": ["Spot 26", "Spot 27"],
        "At a Robotics Table": ["The one by the Closets", "The one by the TV"],
        "In the Living Room": ["Seat 36", "Seat 37", "Seat 38", "Seat 39", "Couch Left", "Couch Right"]
    }

    s = Student.objects.get(id=request.session['sid'])
    etq = s.entryticket_set.filter(date__gte=timezone.now() - timezone.timedelta(hours=12))

    greeting = util.do_greeting(request)
    questions = util.do_questions(request, s)
    music = util.do_music(request)

    return render(request, "classroom/index.html", util.smoosh(SiteConfig.all_configs(), {
        "student": s,
        "greeting": greeting,
        "questions": questions if SiteConfig.objects.get(key="answer_questions") else False,
        "assignments": assignments,
        "seat_options": seats,
        "entry_ticket": SiteConfig.objects.get(key="entry_ticket")
                        and not etq.exists(),
        "covid": SiteConfig.objects.get(key="covid")
                        and not etq.exists(),
        "exit_ticket": SiteConfig.objects.get(key="exit_ticket")
                       and not ExitTicket.objects.filter(student__id=request.session['sid'], date=timezone.now()),
        "music": music,
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
