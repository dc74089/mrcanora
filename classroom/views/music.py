from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.utils import timezone

from classroom import util
from classroom.models import MusicSuggestion


def submit_music(request):
    data = request.POST

    if not util.check_active_student(request):
        return HttpResponseNotAllowed

    if "song_name" not in data or "song_type" not in data:
        return HttpResponseBadRequest()

    suggestion = MusicSuggestion(
        student=util.check_active_student(request),
        song=data['song_name'],
        artist=data.get("song_artist", None),
        for_playlist=data['song_type'] == "class",
    )

    suggestion.save()

    request.session['last_music'] = timezone.now().replace(tzinfo=timezone.utc).timestamp()

    return redirect('index')


def view_music(request):
    by_student = {}

    for sug in MusicSuggestion.objects.filter(investigated=True).exclude(student__homeroom="NA"):
        if sug.student not in by_student:
            by_student[sug.student] = []

        by_student[sug.student].append(sug)

    investigated = sorted([(stu, by_student[stu]) for stu in by_student.keys()], key=lambda x: x[0].lname)

    return render(request, "classroom/music_view.html", {
        "playlist": MusicSuggestion.objects.filter(investigated=False, for_playlist=True).order_by("added"),
        "personal": MusicSuggestion.objects.filter(investigated=False, for_playlist=False).order_by("added"),
        "all": investigated
    })


@login_required
def dismiss(request, id):
    sug = MusicSuggestion.objects.get(id=id)
    sug.investigated = True
    sug.save()

    return redirect('music')


def hide_for_student(request):
    request.session['last_music'] = timezone.now().replace(tzinfo=timezone.utc).timestamp()
    return redirect('index')
