from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, redirect

from classroom import util
from classroom.models import ArtRequest, Student


def ai_index(request):
    s = Student.objects.get(id=request.session['sid'])

    if not util.do_ai(request, s): return HttpResponseForbidden()

    fulfilled = ArtRequest.objects.filter(student__id=s.id, state__gte=8)

    ipq = ArtRequest.objects.filter(student__id=s.id, state__lt=8)
    in_progress = ipq.first() if ipq.exists() else False

    if in_progress:
        try:
            queue = ArtRequest.get_queue()
            ids = [req.id for req in queue]
            queue_pos = ids.index(in_progress.id)
        except ValueError:
            queue_pos = 0
    else:
        queue_pos = 0

    return render(request, "classroom/ai_studio.html", {
        "fulfilled": fulfilled,
        "inprogress": in_progress,
        "resolutions": ArtRequest.resolutions,
        "queuepos": queue_pos,
    })


def new_request(request):
    if request.method != "POST":
        return HttpResponseBadRequest()

    s = Student.objects.get(id=request.session['sid'])
    data = request.POST

    if 'prompt' not in data or 'resolution' not in data:
        return HttpResponseBadRequest()

    req = ArtRequest(student=s, prompt=data['prompt'], resolution=data['resolution'])
    req.save()

    return redirect('ai')


@login_required
def moderate(request):
    data = request.GET

    if 'id' in data and 'action' in data:
        art = ArtRequest.objects.get(id=data['id'])
        if data['action'] == 'approve':
            art.approved = True
            art.state = 10
            art.save()

            return redirect('ai_moderate')
        if data['action'] == 'respin':
            art.state = 4
            art.file = ''
            art.save()

            return redirect('ai_moderate')

    modqueue = ArtRequest.objects.filter(approved=False).exclude(file='')

    return render(request, 'classroom/ai_moderate.html', {
        "modqueue": modqueue
    })
