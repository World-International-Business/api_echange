import uuid
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import Currency


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    reserved_balance = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'currency')

    @property
    def available_balance(self):
        return self.balance - self.reserved_balance

    def __str__(self):
        return f"{self.user.username} - {self.currency_id} ({self.balance})"


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('reserve', 'Reserve'),
        ('release', 'Release'),
        ('fee', 'Fee'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('reversed', 'Reversed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    balance_before = models.DecimalField(max_digits=20, decimal_places=4)
    balance_after = models.DecimalField(max_digits=20, decimal_places=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, db_index=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} {self.amount} - {self.status}"


class Transfer(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=20, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transfers')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transfers')
    sender_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='outgoing_transfers')
    recipient_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='incoming_transfers')
    source_amount = models.DecimalField(max_digits=20, decimal_places=4)
    source_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='transfers_from')
    destination_amount = models.DecimalField(max_digits=20, decimal_places=4)
    destination_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='transfers_to')
    market_rate = models.DecimalField(max_digits=20, decimal_places=8)
    applied_rate = models.DecimalField(max_digits=20, decimal_places=8)
    spread_pct = models.DecimalField(max_digits=6, decimal_places=4)
    fee_amount = models.DecimalField(max_digits=20, decimal_places=4)
    tier = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    sender_transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, related_name='transfer_sent')
    recipient_transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, related_name='transfer_received')
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-initiated_at']

    def __str__(self):
        return f"{self.reference} - {self.source_amount} {self.source_currency_id} → {self.destination_currency_id}"
