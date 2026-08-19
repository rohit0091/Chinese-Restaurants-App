from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def accounts_home(request):
    return HttpResponse("Accounts Page")


