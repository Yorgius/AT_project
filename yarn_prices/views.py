from django.shortcuts import render, HttpResponse

# Create your views here.
def show_charts_home_page(request):
    return HttpResponse('Charts home page')