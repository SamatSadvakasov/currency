#!/bin/bash
celery -A currency.celery worker -l info