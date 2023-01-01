from django.urls import path
from .views import *


app_name = 'yarn_prices_urls'

# The `urlpatterns` list routes URLs to views.
urlpatterns = [
    path('', show_charts_home_page, name='home')
]