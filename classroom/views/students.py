from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect

from classroom.models import Student


def import_students(request):
    if request.method == "POST" and "students" in request.POST:
        in_str = request.POST['students']

        for line in in_str.split("\n"):
            last, first, sid, homeroom = [x.strip() for x in line.split(",")]
            s, created = Student.objects.get_or_create(id=sid)

            s.fname = first
            s.lname = last
            s.grade = int(homeroom[0])
            s.homeroom = homeroom

            s.save()

        return redirect("admin")
    else:
        return HttpResponseBadRequest()


def activate_homeroom(request):
    if request.method != "POST" or "homeroom" not in request.POST:
        return HttpResponseBadRequest()

    hr = request.POST['homeroom']
    grade = hr[:-1]

    for stu in Student.objects.filter(grade=grade):
        stu.enabled = stu.homeroom == hr
        stu.save()

    return redirect("admin")
