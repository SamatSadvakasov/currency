from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction

from .models import ExchangeAgency, CurrencyRate


class AgencyRatesView(LoginRequiredMixin, ListView):
    """View for displaying and managing currency rates for user's exchange agency"""
    model = CurrencyRate
    template_name = 'application/agency_rates.html'
    context_object_name = 'rates'

    def get_queryset(self):
        # Get rates for agencies where user is owner or staff
        return CurrencyRate.objects.filter(
            agency__in=ExchangeAgency.objects.filter(owner=self.request.user)
        ).select_related('agency')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get user's agencies
        context['agencies'] = ExchangeAgency.objects.filter(owner=self.request.user)
        # Group rates by agency
        rates_by_agency = {}
        for rate in context['rates']:
            if rate.agency not in rates_by_agency:
                rates_by_agency[rate.agency] = []
            rates_by_agency[rate.agency].append(rate)
        context['rates_by_agency'] = rates_by_agency
        return context


class CurrencyRateCreateView(LoginRequiredMixin, CreateView):
    """View for creating new currency rates"""
    model = CurrencyRate
    template_name = 'application/currency_rate_form.html'
    fields = ['agency', 'currency', 'buy_rate', 'sell_rate']
    success_url = reverse_lazy('application:agency-rates')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit agency choices to those user has access to
        form.fields['agency'].queryset = ExchangeAgency.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        # Check if user has permission to set rates for this agency
        agency = form.cleaned_data['agency']
        if not (agency.owner == self.request.user or agency.staff.filter(id=self.request.user.id).exists()):
            messages.error(self.request, "You don't have permission to set rates for this agency.")
            return self.form_invalid(form)
        
        try:
            with transaction.atomic():
                # Check if rate already exists for this currency
                existing_rate = CurrencyRate.objects.filter(
                    agency=agency,
                    currency=form.cleaned_data['currency']
                ).first()
                
                if existing_rate:
                    # Update existing rate
                    existing_rate.buy_rate = form.cleaned_data['buy_rate']
                    existing_rate.sell_rate = form.cleaned_data['sell_rate']
                    existing_rate.save()
                    messages.success(self.request, f"Updated {existing_rate.get_currency_display()} rates for {agency.name}")
                else:
                    # Create new rate
                    response = super().form_valid(form)
                    messages.success(
                        self.request, 
                        f"Added {self.object.get_currency_display()} rates for {self.object.agency.name}"
                    )
                    return response
                
                return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Error saving rates: {str(e)}")
            return self.form_invalid(form)
