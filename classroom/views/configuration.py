from django.db.models import ObjectDoesNotExist
from django.http.response import HttpResponseForbidden
from django.shortcuts import redirect

from classroom.models import SiteConfig


def configure(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == "POST":
        for item in SiteConfig.objects.all():
            item.value = False
            item.save()

        for item in request.POST:
            print(item)
            try:
                it = SiteConfig.objects.get(key=item)
                it.value = True
                it.save()
            except ObjectDoesNotExist:
                pass

        return redirect('admin')
