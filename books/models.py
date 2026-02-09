from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

#Category
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


#Genre
class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


#Book
class Book(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='books'
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    isbn = models.CharField(max_length=13, blank=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    language = models.CharField(max_length=50)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)

    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

#Book Inventory
class Inventory(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('requested', 'Requested'),
        ('exchanged', 'Exchanged'),
        ('unavailable', 'Unavailable'),
    ]

    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,
        related_name='inventory'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        db_index=True
    )

    locked_exchange = models.ForeignKey(
        "ExchangeRequest",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    location = models.CharField(max_length=100)

    updated_at = models.DateTimeField(auto_now=True)


#Wishlist
#(API endpoints for wishlist
#Prevent users from wishlisting their own books)

class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} → {self.book.title}"


#ExchangeRequest
class ExchangeRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    requester = models.ForeignKey(User, related_name="sent_requests", on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name="received_requests", on_delete=models.CASCADE)

    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    expected_book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expected_for'
    )

    # requester intent
    requester_wants_cash = models.BooleanField(default=False)

    # owner counter
    is_cash = models.BooleanField(default=False)
    cash_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    requester_confirmed = models.BooleanField(default=False)
    owner_confirmed = models.BooleanField(default=False)

    expires_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_requests"
    )

    reject_reason = models.TextField(blank=True, null=True)

    cancel_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="cancelled")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.pk:
            self.expires_at = timezone.now() + timedelta(hours=48)

        super().save(*args, **kwargs)

        if self.status == "completed":
            Inventory.objects.filter(book=self.book).update(status="exchanged", locked_exchange=None)

            if self.expected_book:
                Inventory.objects.filter(book=self.expected_book).update(status="exchanged", locked_exchange=None)

        if self.status in ["cancelled","rejected","expired"]:
            Inventory.objects.filter(book=self.book).update(status="available", locked_exchange=None)

            if self.expected_book:
                Inventory.objects.filter(book=self.expected_book).update(status="available", locked_exchange=None)

# class Notification(models.Model):

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
#     exchange = models.ForeignKey(ExchangeRequest, on_delete=models.CASCADE)

#     message = models.CharField(max_length=255)

#     is_read = models.BooleanField(default=False)

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.message




