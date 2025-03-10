#!/bin/bash
celery -A currency.celery beat -l info