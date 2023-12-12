import csv
import pprint

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.utils import timezone

from classroom.models import Student, Assignment, Submission


@login_required
def rosters(request):
    tables = {}
    for s in Student.objects.all().exclude(homeroom="NA").order_by("homeroom", "lname"):
        if s.homeroom not in tables:
            tables[s.homeroom] = []

        tables[s.homeroom].append(s)

    return render(request, "classroom/rosters.html", {"tables": tables})


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


def import_bdays(request):
    if request.method == "POST" and "file" in request.FILES:
        fil = request.FILES['file']
        reader = csv.DictReader(fil.read().decode('utf-8').splitlines())
        notfound = 0

        for row in reader:
            try:
                s = Student.objects.get(id__iexact=row['sid'])
                s.bday = timezone.datetime.strptime(row['bday'], "%m/%d/%y")
                s.save()
            except ObjectDoesNotExist:
                notfound += 1
                print(f"Couldn't find {pprint.pformat(dict(row))}")

        print(f"Couldn't find {notfound} students")
        return redirect("admin")
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


def rollover(request):
    if request.method == "GET":
        return render(request, "classroom/rollover.html")
    else:
        for s in Student.objects.all().exclude(id="dc74089").exclude(id="brgoodman"):
            s.grade = -1
            s.homeroom = "NA"
            s.save()

        Assignment.objects.all().delete()
        Submission.objects.all().delete()

        return render(request, "classroom/rollover.html", {"success": True})
