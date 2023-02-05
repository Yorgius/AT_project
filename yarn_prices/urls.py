from django.urls import path
from .views import *


app_name = 'yarn_prices_urls'

# The `urlpatterns` list routes URLs to views.
urlpatterns = [
    path('', show_home_page, name='home'),
    path('charts/', show_charts_page, name='charts'),
    path('charts-data/', charts_data, name='charts_data'),
    # path('loading_data/', save_data_by_bs, name='start_bs'),
]