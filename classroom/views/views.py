import random

from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils import timezone

from classroom import util
from classroom.models import Student, TeambuildingQuestion, SiteConfig, ExitTicket, homerooms


def index(request):
    if not util.check_active_student(request): return redirect("student_login")

    if "greeting" not in request.session:
        last = timezone.datetime.fromtimestamp(0).replace(tzinfo=timezone.utc)
    else:
        last = timezone.datetime.utcfromtimestamp(request.session['greeting_update']).replace(tzinfo=timezone.utc)

    if last + timezone.timedelta(hours=16) < timezone.now():
        greeting = random.choice(["Hey", "Howdy", "What's Up", "Sup", "Hiya", "Merhaba", "Bonjour", "Ahoy",
                                  "Good Morrow", "What's Kickin'", "Hi", "Greetings", "Looking great today",
                                  "Ayyo", "I like ya cut", "How Now", "It's a good day to have a good day",
                                  "Beep Boop", "Hipppity Hoppity", "Hey Now", "It's a beautiful day in paradise",
                                  "Glad to see you", "Owa Owa", "Didn't see you there", "Don't Forget to Be Awesome",
                                  "I'm glad you're here", "I missed you", "Welcome", "**Fun Greeting Here**"])

        request.session['greeting'] = greeting
        request.session['greeting_update'] = timezone.now().replace(tzinfo=timezone.utc).timestamp()
    else:
        greeting = request.session['greeting']

    return render(request, "classroom/index.html", {
        "student": Student.objects.get(id=request.session['sid']),
        "greeting": greeting,
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
