from django.urls import path
from .views import *


app_name = 'yarn_prices_urls'

# The `urlpatterns` list routes URLs to views.
urlpatterns = [
    path('', show_home_page, name='home'),
    path('charts/', show_charts_page, name='charts'),
    path('column-chart-data/', column_chart_data, name='column_chart_data'),
    path('b-line-chart-data/', basic_line_chart_data, name='basic_line_chart_data'),
    # path('charts/show_colors_availability/', show_colors_availability_on_page, name='show_colors_availability'),


    path('ajax_colors/', ajax_colors_list_on_request, name='ajax_colors')
]