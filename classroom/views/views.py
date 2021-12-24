import random

from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone

from classroom import util
from classroom.models import Student, TeambuildingQuestion, SiteConfig, ExitTicket, homerooms, EntryTicket, Assignment


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
                                  "Beep Boop", "Hipppity Hoppity", "Heyyy", "It's a beautiful day in paradise",
                                  "Glad to see you", "Owa Owa", "Didn't see you there", "Don't Forget to Be Awesome",
                                  "I'm glad you're here", "I missed you", "Welcome", "**Fun Greeting Here**"])

        request.session['greeting'] = greeting
        request.session['greeting_update'] = timezone.now().replace(tzinfo=timezone.utc).timestamp()
    else:
        greeting = request.session['greeting']

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

    if s.grade >= -1:
        questions = TeambuildingQuestion.objects.filter(active=True)\
            .filter(grade=s.grade)\
            .exclude(response__student__id=request.session['sid'])
    else:
        questions = TeambuildingQuestion.objects.filter(active=True) \
            .exclude(response__student__id=request.session['sid'])

    return render(request, "classroom/index.html", {
        "student": s,
        "greeting": greeting,
        "questions": questions if SiteConfig.objects.get(key="answer_questions") else False,
        "assignments": assignments,
        "seat_options": seats,
        "entry_ticket": SiteConfig.objects.get(key="entry_ticket")
                        and not etq.exists(),
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
    last = False

    try:
        ans = request.GET.get("answer").strip()
        if ans: ans = ans.lower()
    except:
        ans = ""

    if "escape-progress" not in request.session:
        request.session['escape-progress'] = 0

    progress = request.session['escape-progress']

    if not ans:
        request.session['escape-progress'] = max(progress, 0)

        q = "You'll need to open " \
            "<a href='https://cryptii.com/pipes/md5-hash' target='_blank'>an MD5 Hash Generator</a> and " \
            "<a href='https://terminal.canora.us/' target='_blank'>our hash cracker</a>\n\n" \
            "Find the MD5 hash of <code>yikes</code>."
        e = "658ca1bc659254fc78f8b78ffa9afca6"
    elif ans == "658ca1bc659254fc78f8b78ffa9afca6":
        request.session['escape-progress'] = max(progress, 1)

        q = "Awesome! Write this down: <code>1 = TR</code>\n\n" \
            "What color is missing from this list (<b>There should be 7, and there's only 6</b>)? " \
            "Enter the hash of the missing color:<br><code>" \
            "red: bda9643ac6601722a28f238714274da4\n" \
            "orange: fe01d67a002dfa0f3ac084298142eccd\n" \
            "???: d487dd0b55dfcacdd920ccbdaeafa351\n" \
            "???: 9f27410725ab8cc8854a2769c7a516b8\n" \
            "indigo: 8a99d28c3c43cafed58cdbac5f4e9201\n" \
            "???: d1d813a48d99f0e102f7d0a1b9068001\n" \
            "</code>"
        e = "48d6215903dff56238e52e8891380c8f"
    elif ans == "48d6215903dff56238e52e8891380c8f" or ans == "blue":
        if progress < 1: return HttpResponseBadRequest()
        request.session['escape-progress'] = max(progress, 2)

        q = "Sweet! The missing word was <code>bl</code>ue, so write this down: <code>3 = BL</code>\n\n" \
            "There's a single lowercase letter that has this hash: <code>e1671797c52e15f763380b45e841ec32</code>, " \
            "use our hash cracking tool OR \"guess and check\" to find what it is. Enter the letter:"
        e = "e"
    elif ans == "e":
        if progress < 2: return HttpResponseBadRequest()
        request.session['escape-progress'] = max(progress, 3)

        q = "Yup! It was <code>e</code>, so write this down: <code>4 = E</code>\n\n" \
            "We need to break this hash using our tool now: <code>42239b8342a1fe81a71703f6de711073</code>. " \
            "It's a long one, so let's try the \"common passwords\" mode."
        e = "cactus"
    elif ans == "cactus":
        if progress < 3: return HttpResponseBadRequest()
        request.session['escape-progress'] = max(progress, 4)

        q = "You got it! The password was \"cactus\", <code>ou</code>ch! Write this down: <code>2 = OU</code>\n\n" \
            "Here's an easy one. 1, 2, 3, 4, what word have we formed? Enter it in all lowercase, please:"
        e = "trouble"
    elif ans == "trouble":
        if progress < 4: return HttpResponseBadRequest()
        request.session['escape-progress'] = max(progress, 5)

        q = "Almost there! You've got the word <code>trouble</code>.\n\n" \
            "Write the word trouble using the pigpen cipher. " \
            "Look at your drawing, what's the answer to my math problem?\n\n" \
            "<code>Number of Straight Lines * Number of Dots"
        img = 1
        e = "54"
    elif ans == "54":
        if progress < 5: return HttpResponseBadRequest()
        request.session['escape-progress'] = max(progress, 6)

        q = "The answer is <code>54</code>\n\n" \
            "Look! Our friend is back. " \
            "Letter number <code>5</code> followed by letter number <code>4</code> is the symbol for an element. " \
            "Which one? Enter it in all lowercase, please"
        img = 2
        e = "iron"
    elif ans == "iron":
        if progress < 6: return HttpResponseBadRequest()
        request.session['escape-progress'] = max(progress, 7)

        q = "Iron is correct. We're almost at the <code>end</code> of our <code>game</code>!\n\n" \
            "Fill in the blank: <code>Iron ____</code> and enter its hash. " \
            "You should have enough of a hint already ;)"
        e = "39c63ddb96a31b9610cd976b896ad4f0"
    elif ans == "39c63ddb96a31b9610cd976b896ad4f0":
        if progress < 7: return HttpResponseBadRequest()
        last = True
        word = "cannonball".upper()

        try:
            sid = int(request.session['sid'])
            pos = sid % len(word)
        except (ValueError, KeyError):
            pos = 0

        letter = word[::-1][pos]

        q = "<code>Man</code>, you're good! That was the last step in our search.\n\n" \
            "<b><i>" \
            "It's too late to turn </i>back<i>\n" \
            "So listen to these </i>words<i>,\n" \
            "This riddle doesn't rhyme\n" \
            f"Go write <code>{letter}</code> on the board in slot <code>{pos}</code> if it's not already there.\n\n" \
            f"</i></b>" \
            "Show Mr. Canora this screen, and he will let you know what to do next."

    return render(request, "classroom/pw-escape.html", {
        "question": q,
        "expected": e,
        "image": img,
        "last": last,
    })
