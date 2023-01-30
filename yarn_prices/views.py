from django.shortcuts import render, HttpResponse

# Create your views here.
def show_home_page(request):
    context = [{'title': 'Home'}]
    return render(request, 'yarn_prices/home.html', )


def show_price_charts(request):
    return HttpResponse('Charts page')

def show_charts_page(request):
    return render(request, 'yarn_prices/charts.html')