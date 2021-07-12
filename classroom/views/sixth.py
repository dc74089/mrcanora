from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from django.utils import timezone

from classroom.models import Student, Submission


def tracker(request, group):
    if not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponseForbidden()

    ctx = {'students': []}
    last_week = timezone.now().replace(hour=0, minute=0, second=0) - timezone.timedelta(days=7)
    q = Student.objects.filter(homeroom=group)

    for stu in q:
        stars = 0
        extra_stars = 0
        incomplete = 0
        incomplete_extra = 0

        subs = Submission.objects.filter(student=stu, submitted_at__gte=last_week)
        for sub in subs:
            if sub.satisfactory != "incomplete":
                stars += sub.assignment.name.count("⭐")
                extra_stars += sub.assignment.name.count("✴️")
            else:
                incomplete += sub.assignment.name.count("⭐")
                incomplete_extra += sub.assignment.name.count("✴️")

        ctx['students'].append((stu, range(stars), range(extra_stars), range(incomplete), range(incomplete_extra)))

    return render(request, "classroom/sixth_tracker.html", ctx)
