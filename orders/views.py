from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def orders_home(request):
    return HttpResponse("Your Orders")