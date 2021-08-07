from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render

from ..models import EntryTicket, Student, Assignment, homerooms


def submit(request):
    e = EntryTicket()
    e.student = Student.objects.get(id=request.session['sid'])
    e.seating_location = request.POST.get("location")

    if "objective" in request.POST:
        e.objective = Assignment.objects.get(canvas_id=request.POST.get("objective"))

    e.save()

    return redirect("index")


@staff_member_required
def contact_trace(request):
    ctx = {
        "homerooms": homerooms
    }

    if "homeroom" in request.GET:
        tix = EntryTicket.objects.filter(student__homeroom=request.GET['homeroom'])

        by_date = {}
        for tkt in tix:
            if tkt.date not in by_date:
                by_date[tkt.date] = []

            by_date[tkt.date].append(tkt)

        transformed = []
        for k, arr in by_date.items():
            transformed.append({
                "date": k,
                "objects": sorted(arr, key=lambda x: x.seating_location)
            })

        transformed.sort(key=lambda x: x['date'])
        ctx['tickets'] = transformed

    return render(request, "classroom/contacttrace.html", ctx)
