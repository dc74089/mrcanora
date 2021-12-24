from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from django.utils import timezone

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

        students.append((stu, stars, extra_stars, incomplete))

    return render(request, "classroom/sixth_tracker.html", {
        "students": (students[:(len(students)+1)//2], students[(len(students)+1)//2:]),
        "group": group,
    })
