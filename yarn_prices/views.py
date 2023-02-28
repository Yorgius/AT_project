from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from datetime import datetime
import json

from .models import *
from .scrapers import create_data_set


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
    if not YarnDetails.objects.filter(date=todays_day).exists():
        parse_data_and_save_to_db()
    return render(request, 'yarn_prices/charts.html', context={'title': 'Charts'})

def column_chart_data(request):
    pass
    # # подготовка данных для графика
    # today = datetime.now().date()
    # data_values = []
    # data_set = Yarn.objects.select_related('shop').filter(date_added=today).order_by('price')
    # for yarn in data_set:
    #     # categories.append(yarn.shop.name)
    #     data_values.append([yarn.shop.name, yarn.price])
    
    # # конфигурация данных для графика
    # data = [{
    #     'name': 'Цена',
    #     'data': data_values,
    #     'color': '#FFCCCC',
    #     'dataLabels': {
    #         'enabled': True,
    #         'color': '#000000',
    #         'align': 'center',
    #         'format': '{point.y:.2f}',
    #         # 'y': 0,
    #         'style': {
    #             'fontSize': '10px',
    #         }
    #     }
    # }]

    # # общая конфигурация графика
    # chart = {
    #     'chart': {'type': 'column'},
    #     'legend': {'enabled': False},
    #     'title': {'text': 'Детская новинка', 'align': 'left'},
    #     'subtitle': {'text': today.strftime('%d-%m-%Y'), 'align': 'left'},
    #     'xAxis': {'type': 'category'},
    #     'yAxis': {'min': 0, 'title': {'text': 'BYN'}},
    #     'tooltip': {'pointFormat': "Цена: {point.y:.2f}"},
    #     'series': data,
    # }

    # return JsonResponse(chart)

def basic_line_chart_data(request):
    pass
    # подготовка данных для графика
    # shops = Shop.objects.all()
    
    # data_set = []
    # for shop in shops:
    #     shop_prices_by_time = []
    #     yarns = shop.yarn_set.all().order_by('date_added')
    #     for yarn in yarns:
    #         date = yarn.date_added.strftime('%d-%m-%Y')
    #         shop_prices_by_time.append([date , yarn.price])
    
    #     # конфигурация данных для графика
    #     data_set.append({
    #         'name': shop.name, 
    #         'data': shop_prices_by_time, 
    #         'lineWidth': 2,
    #         'marker': {
    #             'radius': 2, 
    #             'symbol': 'circle'
    #             }
    #         })
    
    # # конфигурация графика
    # chart = {
    #     'title': {
    #         'text': 'Детская новинка',
    #         'align': 'left'
    #     },
    
    #     'subtitle': {
    #         'text': 'г. Минск',
    #         'align': 'left'
    #     },
    
    #     'yAxis': {
    #         'title': {
    #             'text': 'BYN'
    #         }
    #     },
    
    #     'xAxis': {
    #         'type': 'category',
    #         'accessibility': {
    #             'rangeDescription': 'Range: 2010 to 2020'
    #         },
    #         'labels': {
    #             'rotation': -45,
    #             'style': {
    #                 'fontSize': '13px',
    #                 'fontFamily': 'Verdana, sans-serif'
    #             }
    #         }

    #     },
    
    #     'legend': {
    #         'layout': 'horizontal',
    #         'align': 'right',
    #         # 'verticalAlign': 'middle'
    #     },
    
    #     'plotOptions': {
    #         'series': {
    #             'label': {
    #                 'connectorAllowed': 'false'
    #             },
    #         }
    #     },
    
    #     'series': data_set,
    
    #     'responsive': {
    #         'rules': [{
    #             'condition': {
    #                 'maxWidth': 500
    #             },
    #             'chartOptions': {
    #                 'legend': {
    #                     'layout': 'horizontal',
    #                     'align': 'center',
    #                     'verticalAlign': 'bottom'
    #                 }
    #             }
    #         }]
    #     }
    # }

    # return JsonResponse(chart)

# the function starts the BS4 web parser and saves the received data to the database
def parse_data_and_save_to_db() -> None:
    dataset: list = create_data_set()
    for data in dataset:

        try:
            # if Shop.objects.filter(name=data.get('shop')).exists():
            #     shop = Shop.objects.get(name=data.get('shop'))
            # else:
            #     shop = Shop.objects.create(name=data.get('shop'), url=data.get('url'))
            # yarn = Yarn(name=data.get('yarn_name'), price=data.get('yarn_price'), shop=shop)
            # yarn.save()

            if not Shop.objects.filter(name=data.get('shop')).exists():
                shop = Shop.objects.create(name=data.get('shop'), url=data.get('url'))
            else:
                shop = Shop.objects.get(name=data.get('shop'))

            if not YarnCategory.objects.filter(name=data.get('yarn'), shop=shop).exists():
                yarn = YarnCategory.objects.create(name=data.get('yarn'), shop=shop)
            else:
                yarn = YarnCategory.objects.get(name=data.get('yarn'))
            

            YarnDetails.objects.create(yarn=yarn, price=data.get('price'))

            for color in data.get('colors'):
                if not ColorsAvailability.objects.filter(code=color[0], yarn=yarn).exists():
                    ColorsAvailability.objects.create(yarn=yarn, 
                                                    code=color[0], 
                                                    name=color[1], 
                                                    availability=color[2])
                else:
                    color_obj = ColorsAvailability.objects.get(code=color[0], yarn=yarn)
                    color_obj.name = color[1]
                    color_obj.availability = color[2]
                    color_obj.save()

        except Exception as ex:
            print(f'Exception: {ex}')
            print('an exception was thrown while the data was being saved to the database')
            return redirect('yarn_prices_urls:home')
    return redirect('yarn_prices_urls:charts')

