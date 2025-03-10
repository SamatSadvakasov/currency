from django.urls import path, include
from . import views

app_name = 'application'

urlpatterns = [
    path('rates/', views.AgencyRatesView.as_view(), name='agency-rates'),
    path('rates/create/', views.CurrencyRateCreateView.as_view(), name='currency-rate-create'),
    path('rates/<int:pk>/update/', views.CurrencyRateUpdateView.as_view(), name='currency-rate-update'),
    path('rates/<int:pk>/delete/', views.CurrencyRateDeleteView.as_view(), name='currency-rate-delete'),
    path('agency/<int:pk>/', views.AgencyDetailView.as_view(), name='agency-detail'),
]
