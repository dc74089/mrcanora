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
                       and not ExitTicket.objects.filter(student__id=request.session['sid'], date=timezone.now()),
        "escape": SiteConfig.objects.get(key="escape"),
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


def escape(request):
    q = ""
    e = ""
    img = 0

    ans = request.GET.get("answer")

    if not ans:
        q = "Find the MD5 hash of <code>yikes</code>."
        e = "658ca1bc659254fc78f8b78ffa9afca6"
    elif ans == "658ca1bc659254fc78f8b78ffa9afca6":
        q = "Awesome! Write this down: <code>1 = tr</code>\n\n" \
            "There's an item missing from this list. Enter its hash:<br><code>" \
            "red: bda9643ac6601722a28f238714274da4\n" \
            "orange: fe01d67a002dfa0f3ac084298142eccd\n" \
            "???: d487dd0b55dfcacdd920ccbdaeafa351\n" \
            "???: 9f27410725ab8cc8854a2769c7a516b8\n" \
            "indigo: 8a99d28c3c43cafed58cdbac5f4e9201\n" \
            "???: d1d813a48d99f0e102f7d0a1b9068001\n" \
            "</code>"
        e = "48d6215903dff56238e52e8891380c8f"
    elif ans == "48d6215903dff56238e52e8891380c8f":
        q = "You got it! The missing word was <code>bl</code>ue, so write this down: <code>3 = bl</code>\n\n" \
            "There's a single letter that has this hash: <code>e1671797c52e15f763380b45e841ec32</code>, " \
            "either use our hash cracking tool OR \"guess and check\" to find what it is. Enter the letter:"
        e = "e"
    elif ans == "e":
        q = "Yup! It was <code>e</code>, so write this down: <code>4 = e</code>\n\n" \
            "We need to break this hash using our tool now: <code>42239b8342a1fe81a71703f6de711073</code>. " \
            "It's a long one, so let's try the \"common passwords\" mode."
        e = "cactus"
    elif ans == "cactus":
        q = "You got it! The password was \"cactus\", <code>ou</code>ch! Write this down: <code>3 = ou</code>\n\n" \
            "Here's an easy one. 1, 2, 3, 4, what word have we formed? Enter it in all lowercase, please:"
        e = "trouble"
    elif ans == "trouble":
        q = "Almost there! You've got the word <code>trouble</code>.\n\n" \
            "Write the word trouble using the pigpen cipher. " \
            "Look at your drawing, what's the answer to my math problem?\n\n" \
            "<code>Number of Straight Lines * Number of Dots"
        img = 1
        e = "54"
    elif ans == "54":
        q = "The answer is <code>54</code>\n\n" \
            "Look! Our friend is back. " \
            "Letter number <code>5</code> followed by letter number <code>4</code> is the symbol for an element. " \
            "Which one? Enter it in all lowercase, please"
        e = "iron"
    elif ans == "iron":
        q = "We're almost there! "

    return render(request, "classroom/pw-escape.html", {
        "question": q,
        "expected": e,
        "image": img
    })
