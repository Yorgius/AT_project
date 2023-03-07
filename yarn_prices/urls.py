from django.urls import path
from .views import *


app_name = 'yarn_prices_urls'

# The `urlpatterns` list routes URLs to views.
urlpatterns = [
    path('', show_home_page, name='home'),
    path('charts/', show_charts_page, name='charts'),
    path("get-data-for-the-charts", get_data_for_the_charts, name="charts_data"),
    path('ajax_colors/', colors_list_ajax_response, name='ajax_colors'),
]