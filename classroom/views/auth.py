from django.contrib.auth import authenticate, login as do_login, logout as do_logout
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render, redirect


def login(request):
    if request.method == "GET":
        return render(request, 'classroom/login.html', {'next': request.GET.get('next', "")})
    else:
        data = request.POST
        if 'email' in data and 'password' in data:
            user = authenticate(request, username=data['email'], password=data['password'])

            if user is not None:
                do_login(request, user)
                if data.get('next', ""):
                    return redirect(data['next'])

                return redirect('index')
            else:
                return render(request, 'classroom/login.html', {
                    'next': data['next'],
                    'error': "Incorrect username or password."
                })

    return HttpResponseBadRequest()


def logout(request):
    do_logout(request)
    return redirect('index')
