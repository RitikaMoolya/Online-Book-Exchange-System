from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username

#UserPoints
class UserPoints(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='points'
    )

    balance = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.balance} points"


#PointsTransaction
class PointsTransaction(models.Model):
    TRANSACTION_TYPE = [
        ('earn', 'Earn'),
        ('spend', 'Spend'),
        ('refund', 'Refund'),
        ('admin', 'Admin Adjustment'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='point_transactions'
    )

    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)

    reason = models.CharField(max_length=255)

    related_book = models.ForeignKey(
        'books.Book',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.transaction_type} | {self.amount}"
