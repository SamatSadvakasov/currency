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
    list_display = ('agency', 'currency', 'buy_rate', 'sell_rate', 'last_updated')
    list_filter = ('agency', 'currency', 'created_at')
    search_fields = ('agency__name', 'currency')
    readonly_fields = ('created_at', 'changed_at')
    
    def last_updated(self, obj):
        return obj.changed_at_pretty
    last_updated.short_description = 'Last Updated'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('agency')