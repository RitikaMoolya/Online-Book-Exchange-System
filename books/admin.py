from django.contrib import admin
from .models import Book, Category, Genre, Inventory, Wishlist, ExchangeRequest


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "owner",
        "category",
        "genre",
        "language",
        "condition",
        "created_at",
    )

    list_filter = ("category", "genre", "language", "condition")
    search_fields = ("title", "author", "isbn", "owner__username")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("book", "status", "location")
    list_filter = ("status", "location")
    search_fields = ("book__title",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "book")
    search_fields = ("user__username", "book__title")


@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "book",
        "owner",
        "requester",
        "status",
        "expected_book",
        "owner_confirmed",
        "requester_confirmed",
        "created_at",
    )

    list_filter = ("status", "owner_confirmed", "requester_confirmed")
    search_fields = (
        "book__title",
        "owner__username",
        "requester__username",
    )

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)
