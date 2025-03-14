from datetime import datetime
from celery import shared_task
from application.models import ExchangeAgency, CurrencyRate
from application.data.parsing import parse_kurs_kz, parse_mig_kz, parse_chinese_wp


@shared_task
def parsing_task():
    try:
        rate_kurs_kz = parse_kurs_kz()
    except Exception as e:
        print(str(datetime.now()),  e)
        rate_kurs_kz = []

    try:
        rate_mig_kz = parse_mig_kz()
    except Exception as e:
        print(str(datetime.now()),  e)
        rate_mig_kz = []

    try:
        rate_chinese = parse_chinese_wp()
    except Exception as e:
        print(str(datetime.now()),  e)
        rate_chinese = []

    results = {"kurs.kz": rate_kurs_kz, "mig.kz": rate_mig_kz, "china.wp": rate_chinese}
    for agency, rates in results.items():
        a = ExchangeAgency.objects.get(name=agency)
        for currency, buy_rate, sell_rate in rates:
            b, _ = CurrencyRate.objects.get_or_create(agency=a, currency=currency)
            b.buy_rate = buy_rate
            b.sell_rate = sell_rate
            b.changed_at = datetime.now()
            b.save()