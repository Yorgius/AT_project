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
    data_values = []
    # categories = []
    data_set = Yarn.objects.select_related('shop').filter(date_added=datetime.now().date()).order_by('price')
    for yarn in data_set:
        # categories.append(yarn.shop.name)
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
        'legend': {'enabled': False},
        'title': {'text': 'Сравнение цен на пряжу "Детская новинка"', 'align': 'left'},
        'subtitle': {'text': datetime.now().date(), 'align': 'left'},
        # 'xAxis': {'categories': categories},
        'xAxis': {'type': 'category'},
        'yAxis': {'min': 0, 'title': {'text': 'BYN'}},
        'tooltip': {'pointFormat': "Цена: {point.y:.2f}"},
        'series': [data],
    }

    return JsonResponse(chart)

def basic_line_chart_data(request):
    # подготовка данных для графика
    dates = sorted(set(yarn.date_added for yarn in Yarn.objects.all()))
    shops = Shop.objects.all()

    # конфигурация данных для графика
    data_set = []
    for shop in shops:
        shop_prices_by_time = []
        yarns = shop.yarn_set.all().order_by('date_added')
        len_dates = len(dates)
        len_yarns =len(yarns) 
        if not len_dates == len_yarns:
            steps = len_dates - len_yarns
            shop_prices_by_time.extend([None] * steps)
        for yarn in yarns:
            shop_prices_by_time.append(yarn.price)
    
        
        data_set.append({
            'name': shop.name, 
            'data': shop_prices_by_time, 
            'lineWidth': 2,
            'marker': {
                'radius': 2, 
                'symbol': 'circle'
                }
            })
    
    categories = [date.strftime('%d-%m-%Y') for date in dates]

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
            'categories': categories,
            'accessibility': {
                'rangeDescription': 'Range: 2010 to 2020'
            },
            'labels': {
                'rotation': -45,
                'style': {
                    'fontSize': '13px',
                    'fontFamily': 'Verdana, sans-serif'
                }
            }

        },
    
        'legend': {
            'layout': 'horizontal',
            'align': 'right',
            # 'verticalAlign': 'middle'
        },
    
        'plotOptions': {
            'series': {
                'label': {
                    'connectorAllowed': 'false'
                },
                # 'pointStart': xAxis_start_point
            }
        },
    
        'series': data_set,
    
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