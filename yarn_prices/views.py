from django.shortcuts import render, HttpResponse
import json


# main page
def show_home_page(request):
    context = [{'title': 'Home'}]
    return render(request, 'yarn_prices/home.html', )

# визуализация полученных данных в HighCharts
def show_charts_page(request):

    data1 = {
        'name': 'data1',
        'data': [['Tokyo', 37.33], ['Delhi', 31.18], ['Shanghai', 27.79], ['Sao Paulo', 25.23]],
        'color': 'red'
    }

    chart = {
        'chart': {'type': 'column'},
        'legend': {'enabled': True},
        'title': {'text': 'Сравнение цен на пряжу в г. Минске'},
        'xAxis': {'categories': ['Tokyo','Delhi','Shanghai','Sao Paulo']},
        'series': [data1]
    }

    return render(request, 'yarn_prices/charts.html', {'chart': json.dumps(chart)})

