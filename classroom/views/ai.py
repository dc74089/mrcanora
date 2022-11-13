from django.http import HttpResponseForbidden
from django.shortcuts import render

from classroom import util
from classroom.models import ArtRequest, Student


def ai_index(request):
    s = Student.objects.get(id=request.session['sid'])

    if not util.do_ai(request, s): return HttpResponseForbidden()

    fulfilled = ArtRequest.objects.filter(student__id=s.id, state__gte=8)

    ipq = ArtRequest.objects.filter(student__id=s.id, state__lt=8)
    in_progress = ipq.first() if ipq.exists() else False

    return render(request, "classroom/ai_studio.html", {
        "fulfilled": fulfilled,
        "inprogress": in_progress,
        "resolutions": ArtRequest.resolutions
    })


def new_request(request):
    pass  # TODO: This
