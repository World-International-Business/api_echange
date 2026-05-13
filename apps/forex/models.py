from django.db import models
from apps.core.models import Currency


class ForexProvider(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_free = models.BooleanField(default=True)
    weight = models.FloatField(default=1.0)
    priority = models.IntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    last_sync_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return self.name


class ExchangeRate(models.Model):
    from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rates_from')
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rates_to')
    market_rate = models.DecimalField(max_digits=20, decimal_places=8)
    business_rate = models.DecimalField(max_digits=20, decimal_places=8)
    spread = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    margin = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    sources = models.JSONField(default=list)
    fetched_at = models.DateTimeField(auto_now=True)
    is_stale = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_currency', 'to_currency')
        indexes = [
            models.Index(fields=['from_currency', 'to_currency']),
        ]

    def __str__(self):
        return f"{self.from_currency_id}/{self.to_currency_id} = {self.market_rate}"


class RateHistory(models.Model):
    from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='history_from')
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='history_to')
    date = models.DateField()
    open_rate = models.DecimalField(max_digits=20, decimal_places=8)
    high_rate = models.DecimalField(max_digits=20, decimal_places=8)
    low_rate = models.DecimalField(max_digits=20, decimal_places=8)
    close_rate = models.DecimalField(max_digits=20, decimal_places=8)
    avg_rate = models.DecimalField(max_digits=20, decimal_places=8)
    data_points = models.IntegerField(default=0)

    class Meta:
        unique_together = ('from_currency', 'to_currency', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.from_currency_id}/{self.to_currency_id} - {self.date}"
