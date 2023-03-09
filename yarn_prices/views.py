from django.shortcuts import render, redirect
from django.http import JsonResponse
from datetime import datetime

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
    colors_query_set = ColorsAvailability.objects.values('code', 'name').order_by('code')
    colors_set = create_colors_range(colors_query_set)

    context = {
        'title': 'Charts',
        'colors_set': colors_set,
    }
    return render(request, 'yarn_prices/charts.html', context=context)

# подготовка данных для графиков в ответ на ajax запрос
def get_data_for_the_charts(request):
    # Если в базе нет записи с текущей датой
    todays_day = datetime.now().date()

    if not YarnDetails.objects.filter(date=todays_day).exists():
        parse_data_and_save_to_db()

    column_chart = set_column_chart_config()
    line_chart = set_basic_line_chart_config()

    response = {
        'column_chart': column_chart,
        'line_chart': line_chart
    }

    return JsonResponse(response)

# конфигурация столбчатой диаграммы
def set_column_chart_config(shops_list=None) -> dict:
    # подготовка датасета для графика
    today = datetime.now().date()
    data_values = []
    if not shops_list:
        details = YarnDetails.objects.select_related('yarn').filter(date=today).order_by('price')
        for yd in details:
            shop = yd.yarn.shop.name
            data_values.append([shop, yd.price])
    else:
        for shop in shops_list:
            yarn_id = shop.yarncategory_set.get().pk
            details = YarnDetails.objects.get(date=today, yarn=yarn_id)
            data_values.append([shop.name, details.price])
            data_values.sort(key=lambda x: x[1])

    # конфигурация данных для графика series
    data = [{
        'name': 'Цена',
        'data': data_values,
        'color': '#FFCCCC',
        'dataLabels': {
            'enabled': True,
            'color': '#000000',
            'align': 'center',
            'format': '{point.y:.2f}',
            'style': {
                'fontSize': '10px',
            }
        }
    }]

    # общая конфигурация графика
    chart = {
        'chart': {'type': 'column'},
        'legend': {'enabled': False},
        'title': {'text': 'Детская новинка', 'align': 'left'},
        'subtitle': {'text': today.strftime('%d-%m-%Y'), 'align': 'left'},
        'xAxis': {'type': 'category'},
        'yAxis': {'min': 0, 'title': {'text': 'BYN'}},
        'tooltip': {'pointFormat': "Цена: {point.y:.2f}"},
        'series': data,
    }

    return chart

# конфигурация линейных графиков
def set_basic_line_chart_config() -> dict:
    # подготовка датасета для графика
    yarns_categories = YarnCategory.objects.select_related('shop').all()
    data_set = []
    for category in yarns_categories:
        shop_prices_by_time = []
        details = category.yarndetails_set.all().order_by('date')
        for yd in details:
            date = yd.date.strftime('%d-%m-%Y')
            shop_prices_by_time.append([date , yd.price])
    
        # конфигурация данных для графика
        data_set.append({
            'name': category.shop.name, 
            'data': shop_prices_by_time, 
            'lineWidth': 2,
            'marker': {
                'radius': 2, 
                'symbol': 'circle'
                }
            })
    
    # конфигурация графика
    chart = {
        'title': {
            'text': 'Детская новинка',
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
            'type': 'category',
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

    return chart

# the function starts the BS4 web parser and saves the received data to the database
def parse_data_and_save_to_db() -> None:
    dataset: list = create_data_set()
    for data in dataset:
        try:
            if not Shop.objects.filter(name=data.get('shop')).exists():
                shop = Shop.objects.create(name=data.get('shop'), url=data.get('url'))
            else:
                shop = Shop.objects.get(name=data.get('shop'))

            if not YarnCategory.objects.filter(name=data.get('yarn'), shop=shop).exists():
                yarn = YarnCategory.objects.create(name=data.get('yarn'), shop=shop)
            else:
                yarn = YarnCategory.objects.get(name=data.get('yarn'), shop=shop)
            
            YarnDetails.objects.create(yarn=yarn, price=data.get('price'))

            for color in data.get('colors'):
                if not ColorsAvailability.objects.filter(code=color[0], yarn=yarn).exists():
                    ColorsAvailability.objects.create(yarn=yarn, code=int(color[0]), 
                                                    name=color[1], availability=color[2])
                else:
                    color_obj = ColorsAvailability.objects.get(code=int(color[0]), yarn=yarn)
                    color_obj.name = color[1]
                    color_obj.availability = color[2]
                    color_obj.save()

        except Exception as ex:
            print(f'Exception: {ex}')
            print('an exception was thrown while the data was being saved to the database')
            return redirect('yarn_prices_urls:home')
    return redirect('yarn_prices_urls:charts')

# подготовка списка цветов из базы для dropdown list
def create_colors_range(colors_query_set) -> dict:
    colors_set = {}
    for color in colors_query_set:
        if not color['code'] in colors_set.keys():
            colors_set.update({color['code']: color['name']})
    return colors_set

# response для ajax по выбору цвета из dropdown
def colors_list_ajax_response(request) -> dict:
    not_available = ['нет в наличии']

    if request.method == 'POST':
        color_code = int(request.POST.get('submit'))
        colors = ColorsAvailability.objects.select_related('yarn', 'yarn__shop').filter(code=color_code)

        shops_list = []
        available = []
        for color in colors:
            if not color.availability in not_available:
                shop = color.yarn.shop
                available.append({'shop': shop.name, 'shop_url': shop.url, 'availability':  color.availability})
                shops_list.append(shop)

        column_chart = set_column_chart_config(shops_list)

        response = {
            'color_code': color_code,
            'color_name': colors[0].name,
            'available': available,
            'column_chart': column_chart
        }
        return JsonResponse(response)
