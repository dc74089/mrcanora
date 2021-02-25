from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone

from classroom.models import ExitTicket, Student


def submit(request):
    if request.method == "POST" and 'rating' in request.POST:
        data = request.POST

        et = ExitTicket(student_id=request.session['sid'])
        et.understanding = int(data['rating'])
        et.learning_goal = data['learning']
        et.extra = data['extra']
        et.save()

        return redirect('index')
    return HttpResponseBadRequest()


def view(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if 'homeroom' not in request.GET and 'student' not in request.GET:
        return HttpResponseBadRequest()

    if 'date' in request.GET:
        date = timezone.datetime.strptime(request.GET['date'], "%Y-%m-%d").date()

        day_ets = ExitTicket.objects.filter(
            student__homeroom=request.GET['homeroom'], date=date
        ).order_by("student__lname")

        names = [f"{x.student.fname} {x.student.lname}" for x in day_ets]
        ratings = [x.understanding for x in day_ets]

        return render(request, "classroom/analytics_day.html", {
            "names": names,
            "ratings": ratings,
            "tickets": day_ets,
            "student_ids": [x.student.id for x in day_ets]
        })
    elif 'student' in request.GET:
        student_ets = ExitTicket.objects.filter(student__id=request.GET['student'])
        student_ets.order_by("-date")

        names = [str(et.date) for et in student_ets]
        ratings = [et.understanding for et in student_ets]

        return render(request, "classroom/analytics_student.html", {
            "names": names,
            "ratings": ratings,
            "tickets": student_ets,
        })
    else:
        recent_ets = ExitTicket.objects.filter(
            student__homeroom=request.GET['homeroom']
        )

        ets_by_date = {}
        understanding_by_date = {}

        for et in recent_ets:
            if et.date not in ets_by_date:
                ets_by_date[et.date] = []
                understanding_by_date[et.date] = []

            ets_by_date[et.date].append(et)
            understanding_by_date[et.date].append(et.understanding)

        dates = sorted(list(ets_by_date.keys()))
        averages = [sum(understanding_by_date[x])/len(understanding_by_date[x]) for x in dates]

        print(dates, averages)

        return render(request, 'classroom/analytics.html', {
            "dates": [str(x) for x in dates],
            "averages": averages,
            "homeroom": request.GET['homeroom'],
            "students": Student.objects.filter(homeroom=request.GET['homeroom']).order_by("lname", "fname")
        })
