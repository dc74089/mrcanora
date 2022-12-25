import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from classroom import util
from classroom.models import ArtRequest, Student


def ai_index(request):
    s = Student.objects.get(id=request.session['sid'])

    if not util.do_ai(request, s): return HttpResponseForbidden()

    fulfilled = ArtRequest.objects.filter(student__id=s.id, state__range=(8, 10)).reverse()

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
        "student": s,
    })


@login_required
def ai_queue(request):
    queue = list(ArtRequest.get_queue())
    finished = list(ArtRequest.objects.all().exclude(state__lt=6, file=''))

    return render(request, "classroom/ai_queue.html", {
        "queue": queue,
        "finished": finished
    })


def new_request(request):
    if request.method != "POST":
        return HttpResponseBadRequest()

    s = Student.objects.get(id=request.session['sid'])
    data = request.POST

    if 'prompt' not in data or 'resolution' not in data:
        return HttpResponseBadRequest()

    req = ArtRequest(student=s, prompt=data['prompt'], resolution=data['resolution'])

    if 'negative' in data and data['negative']:
        req.set_extra_param('negative_prompt', data['negative'])

    if 'image_in' in request.FILES:
        req.image_in = request.FILES['image_in']
        req.set_extra_param('strength', float(data.get('strength', 0.3)))


    req.save()
    return redirect('ai')


def cancel(request, id):
    req = ArtRequest.objects.get(id=id)

    if req.student == util.check_active_student(request):
        return HttpResponseForbidden()

    if req.is_cancellable():
        req.state = 12
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


def api_get_next_job(request):
    job = ArtRequest.get_next()

    if job:
        return JsonResponse({
            "id": job.id,
            "student_id": job.student.id,
            "prompt": job.prompt,
            "width": job.get_width(),
            "height": job.get_height(),
            "resolution": job.resolution,
            "params": job.get_extra_as_json(),
            "image_in": request.build_absolute_uri(job.image_in_url()),
        })
    else:
        return HttpResponse(status=204)


@csrf_exempt
def api_mark_in_progress(request):
    if not validate_api(request):
        return HttpResponseForbidden()

    if 'id' not in request.POST:
        return HttpResponseBadRequest()

    job = ArtRequest.objects.get(id=request.POST['id'])

    job.state = 6
    job.save()

    return HttpResponse(status=200)


@csrf_exempt
def api_submit_image(request):
    if not validate_api(request):
        return HttpResponseForbidden()

    if 'id' not in request.POST or 'image' not in request.FILES:
        return HttpResponseBadRequest()

    job = ArtRequest.objects.get(id=request.POST['id'])

    job.state = 8
    job.file = request.FILES['image']
    job.save()

    return HttpResponse(status=200)


def validate_api(request):
    return request.POST.get("api_key") == os.getenv('API_KEY', '5821622e-bd3f-4a69-a5cd-88b95646338a')
