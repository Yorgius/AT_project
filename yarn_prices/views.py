from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime
import json

from .models import *
from .scrapers import magic_soup


# main page
def show_home_page(request):
    context = [{'title': 'Home'}]
    return render(request, 'yarn_prices/home.html', )

# визуализация полученных данных в HighCharts
def show_charts_page(request):
    # Если в базе нет записи с текущей датой
    todays_day = datetime.now().date()
    if not Yarn.objects.filter(date_added=todays_day).exists():
        return redirect('yarn_prices_urls:start_bs')
    
    data_values, categories = [], []
    data_set = Yarn.objects.select_related('shop').filter(date_added=todays_day).order_by('price')
    for yarn in data_set:
        categories.append(yarn.shop.name)
        data_values.append([yarn.shop.name, yarn.price])
    # конфигурация графика
    data = {
        'name': 'Цена',
        'data': data_values,
        'color': '#87CEEB',
        'dataLabels': {
            'enabled': True,
            'color': '#FFFFFF',
            'align': 'center',
            'format': '{point.y:.2f}',
            # 'y': 0,
            'style': {
                'fontSize': '10px',
                'fontFamily': 'Verdana, sans-serif'
            }
        }
    }

    chart = json.dumps({
        'chart': {'type': 'column'},
        'legend': {'enabled': True},
        'title': {'text': 'Сравнение цен на пряжу "Детская новинка"'},
        'subtitle': {'text': 'по РБ'},
        'xAxis': {'categories': categories},
        'yAxis': {'min': 0, 'title': {'text': 'BYN'}},
        'legend': {'enabled': False},
        'tooltip': {'pointFormat': "Цена: {point.y:.2f}"},
        'series': [data],
    })

    return render(request, 'yarn_prices/charts.html', {'chart': chart})

def save_data_by_bs(request):
    dataset = magic_soup()
    for data in dataset:
        try:
            if Shop.objects.filter(name=data.get('shop_name')).exists():
                shop = Shop.objects.get(name=data.get('shop_name'))
            else:
                shop = Shop.objects.create(name=data.get('shop_name'),  url=data.get('shop_url'))
            yarn = Yarn(name=data.get('yarn_name'), price=data.get('yarn_price'), shop=shop)
            yarn.save()
        except Exception as exptn:
            print('Вызвано исключение при сохранении нового объекта в БД')
            print(f'Exception: {exptn}')
            return redirect('yarn_prices_urls:home')
    return redirect('yarn_prices_urls:charts')