from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from datetime import datetime
import json

from .models import *
from .scrapers import magic_soup


# main page
def show_home_page(request):
    text = 'With the help of this site, \
        in the graphics section, you can find out where to buy yarn at the best price among the stores in your city, \
            find out the dynamics of yarn price growth, as well as in which store you can buy the colors of yarn you are \
                interested in.'
    return render(request, 'yarn_prices/home.html', context={'title': 'Home', 'description_text': text})

# визуализация полученных данных в HighCharts
def show_charts_page(request):
    # Если в базе нет записи с текущей датой
    todays_day = datetime.now().date()
    if not Yarn.objects.filter(date_added=todays_day).exists():
        save_data_to_db_by_bs()
    return render(request, 'yarn_prices/charts.html', context={'title': 'Charts'})

def column_chart_data(request):
    # подготовка данных для графика
    data_values, categories = [], []
    data_set = Yarn.objects.select_related('shop').filter(date_added=datetime.now().date()).order_by('price')
    for yarn in data_set:
        categories.append(yarn.shop.name)
        data_values.append([yarn.shop.name, yarn.price])
    
    # конфигурация данных для графика
    data = {
        'name': 'Цена',
        'data': data_values,
        'color': '#FFCCCC',
        'dataLabels': {
            'enabled': True,
            'color': '#000000',
            'align': 'center',
            'format': '{point.y:.2f}',
            # 'y': 0,
            'style': {
                'fontSize': '10px',
            }
        }
    }

    # общая конфигурация графика
    chart = {
        'chart': {'type': 'column'},
        'legend': {'enabled': True},
        'title': {'text': 'Сравнение цен на пряжу "Детская новинка"', 'align': 'left'},
        'subtitle': {'text': datetime.now().date(), 'align': 'left'},
        'xAxis': {'categories': categories},
        'yAxis': {'min': 0, 'title': {'text': 'BYN'}},
        'tooltip': {'pointFormat': "Цена: {point.y:.2f}"},
        'series': [data],
    }

    return JsonResponse(chart)

def basic_line_chart_data(request):
    # подготовка данных для графика
    ...
    # конфигурация данных для графика
    data = [{
            'name': 'Installation & Developers',
            'data': [43934, 48656, 65165, 81827, 112143, 142383, 171533, 165174, 155157, 161454, 154610]
        }, 
        {
            'name': 'Manufacturing',
            'data': [24916, 37941, 29742, 29851, 32490, 30282, 38121, 36885, 33726, 34243, 31050]
        }, 
        {
            'name': 'Sales & Distribution',
            'data': [11744, 30000, 16005, 19771, 20185, 24377, 32147, 30912, 29243, 29213, 25663]
        }, 
        {
            'name': 'Operations & Maintenance',
            'data': [None, None, None, None, None, None, None, None, 11164, 11218, 10077],
        }, 
        {
            'name': 'Other',
            'data': [21908, 5548, 8105, 11248, 8989, 11816, 18274, 17300, 13053, 11906, 10073]
        }]
    # конфигурация графика
    chart = {
        'title': {
            'text': 'Динамика изменений цен на пряжу',
            'align': 'left'
        },
    
        'subtitle': {
            'text': 'г. Минск',
            'align': 'left'
        },
    
        'yAxis': {
            'title': {
                'text': 'BYN'
            }
        },
    
        'xAxis': {
            'accessibility': {
                'rangeDescription': 'Range: 2010 to 2020'
            }
        },
    
        'legend': {
            'layout': 'vertical',
            'align': 'right',
            'verticalAlign': 'middle'
        },
    
        'plotOptions': {
            'series': {
                'label': {
                    'connectorAllowed': 'false'
                },
                'pointStart': 2010
            }
        },
    
        'series': data,
    
        'responsive': {
            'rules': [{
                'condition': {
                    'maxWidth': 500
                },
                'chartOptions': {
                    'legend': {
                        'layout': 'horizontal',
                        'align': 'center',
                        'verticalAlign': 'bottom'
                    }
                }
            }]
        }
    }

    return JsonResponse(chart)

# the function starts the BS4 web parser and saves the received data to the database
def save_data_to_db_by_bs() -> None:
    dataset: list = magic_soup()
    for data in dataset:
        try:
            if Shop.objects.filter(name=data.get('shop_name')).exists():
                shop = Shop.objects.get(name=data.get('shop_name'))
            else:
                shop = Shop.objects.create(name=data.get('shop_name'),  url=data.get('shop_url'))
            yarn = Yarn(name=data.get('yarn_name'), price=data.get('yarn_price'), shop=shop)
            yarn.save()
        except Exception as exptn:
            print(f'Exception: {exptn}')
            print('an exception was thrown while the data was being saved to the database')
            return redirect('yarn_prices_urls:home')
    return redirect('yarn_prices_urls:charts')