from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    # return HttpResponse("Welcome to Chinese Center")
    # return render(request, "home/home.html")
    restaurant_name = "Mahato Chinese Center"   #This is called the context.

    return render(
        request,
        "home/home.html",
        {
            "restaurant_name": restaurant_name       #Django template variable, Django replaces it with the value from the context.
        }
    )


def about(request):
    # return HttpResponse("This is the famous restrunt in lohegoan. we have 12+ experienced cooks to serve you any dishes from the menu.")
    return render(request, "home/about.html")

def contact(request):
    return render(request, "home/contact.html")