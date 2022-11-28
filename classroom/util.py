import datetime
import random
from datetime import tzinfo

import pytz
from django.utils import timezone

from classroom.models import Student, TeambuildingQuestion, SiteConfig

seats = {
    "On a Stool": ["On a stool near Alan", "On a stool near the white clock"],
    "In a Desk": ["In a desk by the closets", "In a desk near the TV", "In a desk near the window"],
    "In a Rolling Chair": ["In an office chair under the window", "In a chair around the robot tables"],
    "On the Floor": ["Under the TV", "On the rug"],
    "Other": ["On the Couch"]
}


def smoosh(dict_a, dict_b):
    dict_a.update(dict_b)
    return dict_a


def check_active_student(request):
    if request.user.is_authenticated and request.user.is_staff:
        if 'sid' not in request.session:
            request.session['sid'] = "dc74089"

        obj, created = Student.objects.get_or_create(id="dc74089")
        if created: obj.save()
        return obj

    if "sid" in request.session:
        q = Student.objects.filter(id=request.session['sid'], enabled=True)
        if q.exists():
            return q.first()
        else:
            del request.session['sid']

    return False


def do_greeting(request, student):
    if is_student_bday(student): return "Happy Birthday"

    if "greeting" not in request.session:
        last = timezone.datetime.fromtimestamp(0).replace(tzinfo=timezone.utc)
    else:
        last = timezone.datetime.utcfromtimestamp(request.session['greeting_update']).replace(tzinfo=timezone.utc)

    if last + timezone.timedelta(hours=16) < timezone.now():
        greeting = random.choice(["Hey", "Howdy", "What's Up", "Sup", "Hiya", "Merhaba", "Bonjour", "Ahoy",
                                  "Good Morrow", "What's Kickin'", "Hi", "Greetings", "Looking great today",
                                  "Ayyo", "I like ya cut", "How Now", "It's a good day to have a good day",
                                  "Beep Boop", "Hipppity Hoppity", "Heyyy", "It's a beautiful day in paradise",
                                  "Glad to see you", "Didn't see you there", "Don't Forget to Be Awesome",
                                  "I'm glad you're here", "I missed you", "Welcome", "**Fun Greeting Here**",
                                  "Peek-A-Boo", "'Ello", "This call may be recorded for training purposes",
                                  "We've been trying to reach you regarding your car's extended warranty",
                                  "Greetings and Salutations", "Aloha", "Ciao", "I like your vibe",
                                  "Top of the morning to ya", "Salvē", "Hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",
                                  "Good afternoon. My name is Russell, and I am a Wilderness Explorer in Tribe 54, "
                                  "Sweat Lodge 12. Are you in need of any assistance today", ])

        request.session['greeting'] = greeting
        request.session['greeting_update'] = timezone.now().replace(tzinfo=timezone.utc).timestamp()
    else:
        greeting = request.session['greeting']

    return greeting


def do_questions(request, s):
    if s.grade <= 12:
        questions = TeambuildingQuestion.objects.filter(active=True) \
            .filter(grade=s.grade) \
            .exclude(response__student__id=request.session['sid'])
    else:
        questions = TeambuildingQuestion.objects.all() \
            .exclude(response__student__id=request.session['sid'])

    return questions


def do_music(request, s):
    if s.grade < 6: return False

    if "last_music" not in request.session:
        last = timezone.datetime.fromtimestamp(0).replace(tzinfo=timezone.utc)
    else:
        last = timezone.datetime.utcfromtimestamp(request.session['last_music']).replace(tzinfo=timezone.utc)

    music = SiteConfig.objects.get(key="music").value and (
                "last_music" not in request.session or last + timezone.timedelta(hours=64) < timezone.now())

    return music


def do_ai(request, s):
    if s.grade > 12: return True

    if s.grade == 6:
        if not SiteConfig.objects.get(key="art-6"): return False

        return True
    elif s.grade == 5:
        if not SiteConfig.objects.get(key="art-5"): return False

        return True

    return False


def get_bdays():
    today = timezone.now().astimezone(pytz.timezone("America/New_York"))
    stus = Student.objects.filter(bday__month=today.month, bday__day=today.day, enabled=True)

    return stus


def is_student_bday(student):
    today = timezone.now().astimezone(pytz.timezone("America/New_York"))
    stus = Student.objects.filter(bday__month=today.month, bday__day=today.day, id=student.id)

    return stus.exists()
