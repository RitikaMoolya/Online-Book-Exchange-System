from django.db import models
from django.contrib.auth.models import User

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
    slug = models.SlugField(unique=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='books'
    )

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
        default='available'
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
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    expected_book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        related_name='expected_for'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


