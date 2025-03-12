from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
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
            agency__in=ExchangeAgency.objects.filter(owner=self.request.user, is_external=False)
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


class CurrencyRateUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating existing currency rates"""
    model = CurrencyRate
    template_name = 'application/currency_rate_form.html'
    fields = ['agency', 'currency', 'buy_rate', 'sell_rate']
    success_url = reverse_lazy('application:agency-rates')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['agency'].queryset = ExchangeAgency.objects.filter(owner=self.request.user)
        # Disable currency and agency fields since we're updating
        form.fields['currency'].disabled = True
        form.fields['agency'].disabled = True
        
        # Set initial values from existing rate
        rate = self.get_object()
        form.fields['currency'].initial = rate.currency
        form.fields['agency'].initial = rate.agency
        return form
    
    def get_object(self, queryset=None):
        # Get the rate to update
        return get_object_or_404(CurrencyRate, pk=self.kwargs['pk'])
    
    
    def form_valid(self, form):
        # Check if user has permission to update rates for this agency
        agency = form.cleaned_data['agency']
        if not (agency.owner == self.request.user or agency.staff.filter(id=self.request.user.id).exists()):
            messages.error(self.request, "You don't have permission to update rates for this agency.")
            return self.form_invalid(form)
        
        try:
            with transaction.atomic():
                # Update existing rate
                existing_rate = self.get_object()
                existing_rate.buy_rate = form.cleaned_data['buy_rate']
                existing_rate.sell_rate = form.cleaned_data['sell_rate']
                existing_rate.save()
                messages.success(self.request, f"Updated {existing_rate.get_currency_display()} rates for {agency.name}")
                return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Error updating rates: {str(e)}")
            return self.form_invalid(form)
                


class CurrencyRateDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting existing currency rates"""
    model = CurrencyRate
    template_name = 'application/currency_rate_confirm_delete.html'
    success_url = reverse_lazy('application:agency-rates')


class AgencyDetailView(LoginRequiredMixin, UpdateView):
    """View for displaying and managing currency rates for a specific exchange agency"""
    model = ExchangeAgency
    template_name = 'application/agency_detail.html'
    fields = []  # We don't actually need any fields as we're not editing the agency

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agency = self.get_object()
        
        # Get all user's agencies for the tab navigation
        context['agencies'] = ExchangeAgency.objects.filter(owner=self.request.user, is_external=False)
        
        # Get external rates (e.g., from kurs.kz and mig.kz)
        context['external_rates'] = CurrencyRate.objects.filter(
            agency__is_external=True
        ).select_related('agency')
        
        # Get current agency rates
        context['agency_rates'] = CurrencyRate.objects.filter(
            agency=agency
        ).select_related('agency')
        
        # Create a dictionary of rates by currency for easy access in template

        # Organize external rates by currency
        context['rates_by_currency'] = {
            'USD': {'external': []},

            'EUR': {'external': []},

            'RUB': {'external': []},

            'CNY': {'external': []},

            'USD-CNY': {'external': []},
        }
        for rate in context['external_rates']:
            context['rates_by_currency'][rate.currency]['external'].append(rate)

        # Add agency rates
        for rate in context['agency_rates']:
            context['rates_by_currency'][rate.currency]['agency'] = rate
        
        return context

    def get_queryset(self):
        # Only allow access to user's own agencies
        return ExchangeAgency.objects.filter(owner=self.request.user)
    
    