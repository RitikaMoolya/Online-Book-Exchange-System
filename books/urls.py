from django.urls import path
from . import views

urlpatterns = [
    path("explore/", views.explore_books, name="explore_books"),
    path("upload/", views.upload_book, name="upload_book"),
    path("books/<slug:slug>/", views.book_detail, name="book_detail"),
    path("my-books/", views.my_uploaded_books, name="my_uploaded_books"),
    path("books/edit/<int:pk>/", views.edit_book, name="edit_book"),
    path("books/delete/<int:pk>/", views.delete_book, name="delete_book"),
    path("request/<slug:slug>/", views.request_exchange, name="request_exchange"),
    path("check/",views.check_notifications,name="check"),
    path("requests/", views.notifications, name="notifications"),
    path("confirm/<int:pk>/", views.confirm_exchange, name="confirm_exchange"),
    path("approve/<int:id>/", views.approve_request, name="approve_request"),
    path("reject/<int:id>/", views.reject_request, name="reject_request"),
    path("accept/<int:pk>/", views.accept_deal, name="accept_deal"),
    path("reject-deal/<int:pk>/", views.reject_deal, name="reject_deal"),
    path("cancel/<int:pk>/", views.cancel_exchange, name="cancel_exchange"),
    path("requested/", views.view_requested_books, name="view_requested_books"),
    path("exchanged/", views.view_exchanged_books, name="view_exchanged_books"),
    path("exchange-status/<int:pk>/", views.exchange_status, name="exchange_status"),
    path("request-cash/<int:pk>/",views.request_cash,name="request_cash"),
    path("approve-cash/<int:pk>/", views.approve_cash, name="approve_cash")
]
