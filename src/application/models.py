import datetime as dt
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _



class TimestampModel(models.Model):
    """Timestamp model"""

    created_at: dt.datetime = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created at")
    )
    changed_at: dt.datetime = models.DateTimeField(
        auto_now=True, verbose_name=_("Changed at")
    )

    @property
    def created_at_pretty(self):
        return self.created_at.strftime("%d.%m.%Y %H:%M:%S")

    @property
    def changed_at_pretty(self):
        return self.changed_at.strftime("%d.%m.%Y %H:%M:%S")

    class Meta:
        abstract = True


class ExchangeAgency(TimestampModel):
    """Model to store information about exchange agencies"""
    
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Agency name"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))
    is_external = models.BooleanField(default=False, verbose_name=_("Is external source"))
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exchange_agencies',
        verbose_name=_("Agency Owner")
    )
    staff = models.ManyToManyField(
        User,
        related_name='staffed_agencies',
        verbose_name=_("Agency Staff"),
        blank=True
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Exchange Agency")
        verbose_name_plural = _("Exchange Agencies")


class CurrencyRate(TimestampModel):
    """Model to store currency rates for exchange agencies"""
    
    CURRENCY_CHOICES = [
        ('USD', _('US Dollar')),
        ('EUR', _('Euro')),
        ('RUB', _('Russian Ruble')),
        ('CNY', _('China Yuan')),
        ('USD-CNY', _('USD - Yuan (美元)')),
    ]
    
    agency = models.ForeignKey(
        ExchangeAgency,
        on_delete=models.CASCADE,
        related_name='currency_rates',
        verbose_name=_("Exchange Agency")
    )
    currency = models.CharField(
        max_length=7,
        choices=CURRENCY_CHOICES,
        verbose_name=_("Currency")
    )
    buy_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Buy Rate"),
        null=True,
        blank=True,
    )
    sell_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Sell Rate"),
        null=True,
        blank=True,
    )
    
    def __str__(self):
        return f"{self.agency.name} - {self.currency}"
    
    class Meta:
        verbose_name = _("Currency Rate")
        verbose_name_plural = _("Currency Rates")
        unique_together = ['agency', 'currency']  # Each agency can have only one rate per currency



