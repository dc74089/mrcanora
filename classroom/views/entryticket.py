import re

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.utils import timezone

from ..models import EntryTicket, Student, Assignment, homerooms


def submit(request):
    e = EntryTicket()
    e.student = Student.objects.get(id=request.session['sid'])
    e.seating_location = request.POST.get("location")

    if "objective" in request.POST:
        e.objective = Assignment.objects.get(canvas_id=request.POST.get("objective"))

    e.save()

    return redirect("index")


def contact_trace(request):
    ctx = {
        "homerooms": homerooms
    }

    if "homeroom" in request.GET:
        tix = EntryTicket.objects.filter(student__homeroom=request.GET['homeroom'])

        by_date = {}
        for tkt in tix:
            date = tkt.date.date()
            if date not in by_date:
                by_date[date] = []

            by_date[date].append(tkt)

        transformed = []
        for k, arr in by_date.items():
            transformed.append({
                "date": k,
                "objects": sorted(arr, key=lambda x: sort_locations(x.seating_location))
            })

        transformed.sort(key=lambda x: x['date'], reverse=True)
        ctx['tickets'] = transformed

    return render(request, "classroom/contacttrace.html", ctx)


def sort_locations(loc):
    match = re.search(r'\d+', loc)
    if match:
        return match[0]

    return loc


@staff_member_required
def entryticket_status(request):
    homeroom = request.GET['homeroom']

    sq = Student.objects.filter(homeroom__iexact=homeroom).order_by("fname")
    sarr = []
    for s in sq:
        etq = s.entryticket_set.filter(date__gte=timezone.now() - timezone.timedelta(hours=12))
        sarr.append((s, etq.exists()))

    print(sarr)
    print((sarr[:(len(sarr)+1)//2], sarr[(len(sarr)+1)//2:]))

    return render(request, "classroom/entryticket_status.html", {
        "homeroom": homeroom,
        "tables": (sarr[:(len(sarr)+1)//2], sarr[(len(sarr)+1)//2:])
    })
