from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from classroom.models import Student, Submission


def tracker(request, group):
    students = []
    q = Student.objects.filter(homeroom=group).order_by("fname")

    for stu in q:
        stars = 0
        extra_stars = 0
        incomplete = 0
        group = stu.get_homeroom_display()

        subs = Submission.objects.filter(student=stu)
        for sub in subs:
            if sub.satisfactory != False:
                stars += sub.assignment.name.count("⭐")
                extra_stars += sub.assignment.name.count("✴")

        students.append((stu, stars, extra_stars, incomplete, stars + extra_stars - stu.used_stars))

    return render(request, "classroom/sixth_tracker.html", {
        "students": (students[:(len(students)+1)//2], students[(len(students)+1)//2:]),
        "group": group,
    })


@csrf_exempt
@login_required
def spend_stars(request):
    if request.method == "POST":
        data = request.POST
        if "student" not in data or "numstars" not in data:
            return HttpResponseBadRequest()

        sq = Student.objects.filter(id=data['student'])

        if not sq.exists():
            return HttpResponseBadRequest()

        stu = sq.first()
        stu.used_stars += int(data['numstars'])
        stu.save()

        return redirect('sixth_spend_stars')

    ctx = {
        "students": Student.objects.filter(grade=6, enabled=True).order_by("fname")
    }

    return render(request, "classroom/sixth_spend_stars.html", ctx)
