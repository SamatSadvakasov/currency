from django.contrib import admin
from django.utils.html import format_html
from .models import ExchangeAgency, CurrencyRate


@admin.register(ExchangeAgency)
class ExchangeAgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_info', 'staff_count', 'is_active', 'is_external', 'created_at_pretty')
    list_filter = ('is_active', 'is_external', 'created_at')
    search_fields = ('name', 'owner__username', 'staff__username')
    readonly_fields = ('created_at', 'changed_at')
    
    def owner_info(self, obj):
        return format_html(
            '<span style="color: #1a73e8;">{}</span>',
            obj.owner.username
        )
    owner_info.short_description = 'Owner'
    
    def staff_count(self, obj):
        count = obj.staff.count()
        return format_html(
            '<span style="color: {};">{} staff member{}</span>',
            '#28a745' if count > 0 else '#dc3545',
            count,
            's' if count != 1 else ''
        )
    staff_count.short_description = 'Staff Members'


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ('agency', 'currency', 'buy_rate_display', 'sell_rate_display', 'margin', 'last_updated')
    list_filter = ('agency', 'currency', 'created_at')
    search_fields = ('agency__name', 'currency')
    readonly_fields = ('created_at', 'changed_at')
    
    def buy_rate_display(self, obj):
        return format_html(
            '<span style="color: #28a745;">{:.2f}</span>',
            obj.buy_rate
        )
    buy_rate_display.short_description = 'Buy Rate'
    
    def sell_rate_display(self, obj):
        return format_html(
            '<span style="color: #dc3545;">{:.2f}</span>',
            obj.sell_rate
        )
    sell_rate_display.short_description = 'Sell Rate'
    
    def margin(self, obj):
        margin = obj.sell_rate - obj.buy_rate
        return format_html(
            '<span style="color: {};">{:.2f}</span>',
            '#28a745' if margin > 0 else '#dc3545',
            margin
        )
    margin.short_description = 'Margin'
    
    def last_updated(self, obj):
        return obj.changed_at_pretty
    last_updated.short_description = 'Last Updated'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('agency')