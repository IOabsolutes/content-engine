from django.shortcuts import render

# Create your views here.


def home_page_view(request):
    return render(request, "landing/home.html", {})


def about_page_view(request):
    return render(request, "landing/about.html", {})