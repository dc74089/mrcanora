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

    hr = [request.POST['homeroom']]
    grade = hr[0][:-1]

    if grade == '6':
        if hr[0] == "6A": hr.append("6B")
        if hr[0] == "6B": hr.append("6A")
        if hr[0] == "6C": hr.append("6D")
        if hr[0] == "6D": hr.append("6C")
        if hr[0] == "6E": hr.append("6F")
        if hr[0] == "6F": hr.append("6E")
        if hr[0] == "6G": hr.append("6H")
        if hr[0] == "6H": hr.append("6G")

    for stu in Student.objects.filter(grade=grade):
        stu.enabled = stu.homeroom in hr
        stu.save()

    return redirect("admin")
