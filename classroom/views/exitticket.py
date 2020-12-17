from django.http import HttpResponseBadRequest
from django.shortcuts import redirect

from classroom.models import ExitTicket


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
