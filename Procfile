web: cd forex_platform && python manage.py migrate --settings=forex_platform.settings && gunicorn forex_platform.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
