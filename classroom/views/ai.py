import itertools
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.templatetags.static import static
from django.views.decorators.csrf import csrf_exempt

from classroom import util
from classroom.models import ArtRequest, Student, homerooms


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


def exemplars(request):
    positive = [
        "trending on artstation",
        "beautiful",
        "ultra detailed",
        "best one yet",
        "symmetrical (only if it makes sense)",
        "ethereal (means light, airy, etc... only if it makes sense)",
    ]

    negative = [
        "black and white",
        "bad anatomy",
        "deformed",
        "extra limbs",
        "too many legs",
        "too many hands",
        "too bright",
        "too dark",
    ]

    return render(request, "classroom/ai_exemplars.html", {
        "arts": ArtRequest.objects.filter(exemplar=True),
        "artists": [
            ("Alan Lee", static("classroom/artist_study/Alan Lee.png")),
            ("Andy Warhol", static("classroom/artist_study/Andy Warhol.png")),
            ("Banksy", static("classroom/artist_study/Banksy.png")),
            ("Dali", static("classroom/artist_study/Dali.png")),
            ("Degas", static("classroom/artist_study/Degas.png")),
            ("Ismail Inceoglu", static("classroom/artist_study/Ismail Inceoglu.jpeg")),
            ("Makoto Shinkai", static("classroom/artist_study/Makoto Shinkai.jpg")),
            ("Monet", static("classroom/artist_study/Monet.png")),
            ("Picasso", static("classroom/artist_study/Picasso.png")),
            ("Qinni", static("classroom/artist_study/Qinni.jpeg")),
            ("Sparth", static("classroom/artist_study/Sparth.jpeg")),
            ("Van Gogh", static("classroom/artist_study/Van Gogh.png")),
        ],
        "keywords": itertools.zip_longest(positive, negative)
    })


@csrf_exempt
@login_required
def choose_featured(request):
    if request.method == "GET":
        if 'homeroom' in request.GET:
            images_q = ArtRequest.objects.filter(student__homeroom=request.GET.get("homeroom", ""))
            images = {}

            for req in images_q:
                if req.student not in images:
                    images[req.student] = []

                images[req.student].append(req)

            return render(request, "classroom/ai_choose_featured.html", {
                "homeroom": request.GET.get("homeroom"),
                "homerooms": homerooms,
                "images": images,
            })
        else:
            return render(request, "classroom/ai_choose_featured.html", {
                "homerooms": homerooms
            })
    else:
        data = request.POST

        if 'id' in data and 'feature' in data:
            req = ArtRequest.objects.get(id=data['id'])
            req.feature_photo = True if data['feature'] == 'true' else False
            req.save()

            return HttpResponse(status=200)



def all_features(request):
    iq = ArtRequest.objects.filter(feature_photo=True)

    if 'homeroom' in request.GET:
        iq.filter(student__homeroom=request.GET['homeroom'])

    return render(request, "classroom/ai_featured.html", {
        "images": iq
    })


def training(request):
    return render(request, "classroom/ai_training.html")


@login_required
def ai_queue(request):
    queue = list(ArtRequest.get_queue())
    finished = reversed(list(ArtRequest.objects.all().exclude(state__lte=6, file='')))

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
        req.negative_prompt = data['negative']

    if 'guidance' in data:
        req.set_extra_param('guidance_scale', float(data['guidance']))

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
            "negative": job.negative_prompt,
            "width": job.get_width(),
            "height": job.get_height(),
            "resolution": job.resolution,
            "params": job.get_extra_with_negative(),
            "image_in": request.build_absolute_uri(job.image_in_url()) if job.image_in_url() else False,
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
