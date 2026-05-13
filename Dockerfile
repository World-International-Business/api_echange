FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/forex_platform

RUN python manage.py collectstatic --noinput --settings=forex_platform.settings 2>/dev/null || true

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --settings=forex_platform.settings && gunicorn forex_platform.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120"]
