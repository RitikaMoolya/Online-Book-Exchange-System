from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .forms import BookForm
from django.db import transaction
from .models import Book, Category, Genre, Inventory, ExchangeRequest

@login_required
def explore_books(request):

    books = Book.objects.filter(
        ~Q(exchangerequest__status__in=["approved", "completed"])
    ).distinct().select_related("category", "genre")

    return render(request, "books/explore_books.html", {
        "books": books
    })

@login_required
def book_detail(request, slug):

    book = get_object_or_404(Book, slug=slug)

    exchange = ExchangeRequest.objects.filter(
        book=book,
        # status__in=["pending", "approved"]
    ).order_by("-created_at").first()

    return render(request, "books/book_detail.html", {
        "book": book,
        "exchange": exchange
    })

@login_required
def upload_book(request):

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)

        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user

            # slug
            base_slug = slugify(book.title)
            slug = base_slug
            c = 1
            while Book.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{c}"
                c += 1
            book.slug = slug

            # Custom Category
            if form.cleaned_data["category"].name == "Others":
                cat,_ = Category.objects.get_or_create(
                    name=form.cleaned_data["custom_category"]
                )
                book.category = cat

            # Custom Genre
            if form.cleaned_data["genre"].name == "Others":
                gen,_ = Genre.objects.get_or_create(
                    name=form.cleaned_data["custom_genre"]
                )
                book.genre = gen

            book.save()

            # ✅ Auto Inventory
            Inventory.objects.create(
                book=book,
                status="available",
                # location=form.cleaned_data["location"]
            )

            messages.success(request,"Book uploaded successfully!")
            return redirect("explore_books")

    else:
        form = BookForm()

    return render(request,"books/upload_book.html",{"form":form})

@login_required
def my_uploaded_books(request):
    books = Book.objects.filter(owner=request.user).order_by("-created_at")

    return render(request, "books/my_uploaded_books.html", {
        "books": books
    })

@login_required
def edit_book(request, pk):

    book = get_object_or_404(Book, pk=pk, owner=request.user)

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)

        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully.")
            return redirect("my_uploaded_books")

    else:
        form = BookForm(instance=book)

    return render(request, "books/edit_book.html", {
        "form": form,
        "book": book
    })

@login_required
def delete_book(request, pk):

    book = get_object_or_404(Book, pk=pk, owner=request.user)

    if request.method == "POST":
        book.delete()
        messages.error(request, "Book deleted successfully.")

    return redirect("my_uploaded_books")

@login_required
def request_exchange(request, slug):

    book = get_object_or_404(Book, slug=slug)

    if book.owner == request.user:
        return redirect("book_detail", slug=slug)

    if ExchangeRequest.objects.filter(book=book, status__in=["pending","approved"]).exists():
        messages.error(request,"Already requested.")
        return redirect("book_detail", slug=slug)

    wants_cash = request.GET.get("cash")

    ExchangeRequest.objects.create(
        requester=request.user,
        owner=book.owner,
        book=book,
        requester_wants_cash=bool(wants_cash),
        is_cash=False,
        cash_amount=book.price if wants_cash else None
    )

    # Inventory.objects.filter(book=book).update(status="requested")

    messages.success(
        request,
        "Request sent. Owner will review your offer."
    )

    return redirect("book_detail", slug=slug)

@login_required
def notifications(request):

    requests = ExchangeRequest.objects.filter(owner=request.user).order_by("-created_at")

    return render(request,"books/notifications.html",{"requests":requests})

@login_required
def approve_request(request,id):

    r = get_object_or_404(ExchangeRequest,id=id, owner=request.user)

    if r.status != "pending":
        messages.warning(request, "Already handled.")
        return redirect("notifications")

    expected = request.POST.get("expected")

    r.expected_book_id = expected
    r.is_cash = False
    r.cash_amount = None

    # ❌ DO NOT APPROVE HERE
    # r.status = "approved"

    r.save()

    Inventory.objects.filter(book=r.book).update(status="requested", locked_exchange=r)
    Inventory.objects.filter(book_id=expected).update(status="requested", locked_exchange=r)

    messages.success(request,"Offer sent. Waiting for requester confirmation.")

    return redirect("notifications")

@login_required
def reject_request(request, id):

    r = get_object_or_404(ExchangeRequest, id=id, owner=request.user)

    if r.status != "pending":
        messages.warning(request, "This request can no longer be rejected.")
        return redirect("notifications")

    r.status = "rejected"
    r.rejected_by = request.user
    r.reject_reason = request.POST.get("reason")
    r.save()

    Inventory.objects.filter(book=r.book).update(
        status="available",
        locked_exchange=None
    )

    if r.expected_book:
        Inventory.objects.filter(book=r.expected_book).update(
            status="available",
            locked_exchange=None
        )

    messages.error(request, "Request rejected.")

    return redirect("notifications")

@login_required
def confirm_exchange(request, pk):

    r = get_object_or_404(ExchangeRequest, pk=pk)

    if request.user not in [r.owner, r.requester]:
        return redirect("notifications")

    if r.status != "approved":
        messages.warning(request, "This deal is not approved yet.")
        return redirect("notifications")

    if request.user == r.owner:
        r.owner_confirmed = True

    if request.user == r.requester:
        r.requester_confirmed = True

    # ONLY when both confirm → complete + exchange inventory
    if r.owner_confirmed and r.requester_confirmed:

        r.status = "completed"

        Inventory.objects.filter(book=r.book).update(
            status="exchanged",
            locked_exchange=None
        )

        if r.expected_book:
            Inventory.objects.filter(book=r.expected_book).update(
                status="exchanged",
                locked_exchange=None
            )

    r.save()

    messages.success(request, "Marked as received.")

    if request.user == r.owner:
        return redirect("notifications")
    else:
        return redirect("view_requested_books")

@login_required
def accept_deal(request, pk):

    r = get_object_or_404(
        ExchangeRequest,
        pk=pk,
        requester=request.user
    )

    if r.status != "pending":
        messages.warning(request, "Deal already handled.")
        return redirect("view_requested_books")

    with transaction.atomic():

        # ✅ Approve THIS request
        r.requester_accepted = True
        r.status = "approved"
        r.save()

        # 🔒 Lock inventory for approved exchange
        Inventory.objects.filter(book=r.book).update(
            status="requested",
            locked_exchange=r
        )

        if r.expected_book:
            Inventory.objects.filter(book=r.expected_book).update(
                status="requested",
                locked_exchange=r
            )

        # ❌ Auto-reject ALL OTHER pending requests for same book
        ExchangeRequest.objects.filter(
            book=r.book,
            status="pending"
        ).exclude(id=r.id).update(
            status="rejected",
            rejected_by=r.owner,
            reject_reason="Another request for this book was approved."
        )

    messages.success(request, "Deal accepted. Contact owner to proceed.")
    return redirect("view_requested_books")

@login_required
def reject_deal(request, pk):

    r = get_object_or_404(
        ExchangeRequest,
        pk=pk,
        requester=request.user
    )

    if r.status != "pending":
        messages.warning(request, "Deal can no longer be rejected.")
        return redirect("view_requested_books")

    if request.method == "POST":

        r.status = "rejected"
        r.rejected_by = request.user
        r.reject_reason = request.POST.get("reason")
        r.save()

        Inventory.objects.filter(book=r.book).update(
            status="available",
            locked_exchange=None
        )

        if r.expected_book:
            Inventory.objects.filter(book=r.expected_book).update(
                status="available",
                locked_exchange=None
            )

        messages.error(request, "Deal rejected.")

    return redirect("view_requested_books")

@login_required
def cancel_exchange(request, pk):

    r = get_object_or_404(ExchangeRequest, pk=pk)

    if request.user not in [r.owner, r.requester]:
        return redirect("explore_books")

    if r.status in ["completed", "rejected", "cancelled"]:
        messages.warning(request, "This exchange can no longer be cancelled.")
        return redirect(
            "notifications" if request.user == r.owner else "view_requested_books"
        )

    if request.method == "POST":

        r.status = "cancelled"
        r.cancel_reason = request.POST.get("reason")
        r.cancelled_by = request.user
        r.save()

        Inventory.objects.filter(book=r.book).update(
            status="available",
            locked_exchange=None
        )

        if r.expected_book:
            Inventory.objects.filter(book=r.expected_book).update(
                status="available",
                locked_exchange=None
            )

        messages.error(request, "Deal cancelled.")

    # ✅ redirect based on who cancelled
    if request.user == r.owner:
        return redirect("notifications")
        messages.error(request, "You cancelled this exchange.")
    else:
        return redirect("view_requested_books")
        messages.error(request, "You cancelled this exchange.")


@login_required
def request_cash(request, pk):

    r = get_object_or_404(ExchangeRequest, pk=pk, owner=request.user)

    r.is_cash = True
    r.cash_amount = r.book.price
    r.expected_book = None
    r.save()

    messages.warning(
        request,
        f"You offered cash ₹{r.cash_amount} instead of exchange."
    )

    return redirect("notifications")

@login_required
def approve_cash(request, pk):

    r = get_object_or_404(
        ExchangeRequest,
        pk=pk,
        owner=request.user,
        requester_wants_cash=True,
        status="pending"
    )

    r.is_cash = True
    r.status = "approved"
    r.save()

    Inventory.objects.filter(book=r.book).update(
        status="requested",
        locked_exchange=r
    )

    # 🔥 auto-reject other pending requests
    ExchangeRequest.objects.filter(
        book=r.book,
        status="pending"
    ).exclude(id=r.id).update(
        status="rejected",
        rejected_by=request.user,
        reject_reason="Another offer was accepted."
    )

    messages.success(request, "Cash purchase approved.")

    return redirect("notifications")

@login_required
def exchange_status(request, pk):
    r = get_object_or_404(ExchangeRequest, pk=pk)

    return JsonResponse({
        "status": r.status,
        "owner_confirmed": r.owner_confirmed,
        "requester_confirmed": r.requester_confirmed,
    })

@login_required
def check_notifications(request):

    count = ExchangeRequest.objects.filter(owner=request.user,status="pending").count()

    return JsonResponse({"count":count})

@login_required
def view_requested_books(request):

    exchanges = ExchangeRequest.objects.filter(
        requester=request.user
    ).select_related(
        "book",
        "expected_book",   # ✅ ADD THIS
        "owner"
    ).order_by("-created_at")

    return render(request, "books/view_requested_books.html", {
        "exchanges": exchanges
    })

@login_required
def view_exchanged_books(request):
    exchanges = ExchangeRequest.objects.filter(
        status="completed"
    ).filter(
        Q(requester=request.user) | Q(owner=request.user)
    ).select_related("book").order_by("-created_at")

    return render(request, "books/view_exchanged_books.html", {
        "exchanges": exchanges
    })
