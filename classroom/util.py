from classroom.models import Student


def check_active_student(request):
    if request.user.is_authenticated and request.user.is_staff:
        if 'sid' not in request.session:
            request.session['sid'] = "dc74089"
            obj, created = Student.objects.get_or_create(id="dc74089")
            if created: obj.save()
        return True

    if "sid" in request.session:
        if Student.objects.filter(id=request.session['sid'], enabled=True).exists():
            return True
        else:
            del request.session['sid']

    return False
