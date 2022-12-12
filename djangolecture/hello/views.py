from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return HttpResponse("Hello, World!")


def sabmus(request):
    return HttpResponse("Hello, Sabmus!")


def simon(request):
    return HttpResponse("Hello, Simón!")


def greet(request, name):
    return render(request, "hello/greet.html", {
        "name": name.capitalize()
    })


def new_index(request):
    return render(request, "hello/index.html")
