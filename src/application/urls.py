from django.urls import path, include
from . import views

app_name = 'application'

urlpatterns = [
    path('rates/', views.AgencyRatesView.as_view(), name='agency-rates'),
    path('rates/create/', views.CurrencyRateCreateView.as_view(), name='currency-rate-create'),
]
