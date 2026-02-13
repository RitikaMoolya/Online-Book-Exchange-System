from django import forms
from .models import Book, Category, Genre
from django.db.models import Case, When, Value, IntegerField

class BookForm(forms.ModelForm):

    custom_category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter category"
        })
    )

    custom_genre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter genre"
        })
    )

    location = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your City"
        })
    )

    price = forms.DecimalField(
    required=False,
    widget=forms.NumberInput(attrs={
        "class":"form-control",
        "placeholder":"Price"
    })
    )


    class Meta:
        model = Book
        fields = [
            "title", "author", "description", "isbn",
            "category", "genre", "custom_category", "custom_genre",
            "language", "condition", "location", "cover_image", "price"
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Book title"}),
            "author": forms.TextInput(attrs={"class": "form-control", "placeholder": "Author"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Description"}),
            "isbn": forms.TextInput(attrs={"class": "form-control", "placeholder": "ISBN"}),
            "language": forms.TextInput(attrs={"class": "form-control", "placeholder": "Language"}),
            "cover_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control placeholder-select", "id": "category"}),
            "genre": forms.Select(attrs={"class": "form-control placeholder-select", "id": "genre"}),
            "condition": forms.Select(attrs={"class": "form-control placeholder-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only first 10 records
        self.fields["category"].queryset = Category.objects.all()
        self.fields["genre"].queryset = Genre.objects.all()

        self.fields["category"].queryset = Category.objects.annotate(
            is_other=Case(
                When(name="Others", then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by("is_other", "name")

        self.fields["genre"].queryset = Genre.objects.annotate(
            is_other=Case(
                When(name="Others", then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by("is_other", "name")

        # Placeholder
        self.fields["category"].choices = [("", "Category")] + list(self.fields["category"].choices)
        self.fields["genre"].choices = [("", "Genre")] + list(self.fields["genre"].choices)

        # Condition placeholder
        self.fields["condition"].choices = [("", "Condition")] + list(
            self.fields["condition"].choices
        )

    # =====================
    # Validation
    # =====================

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get("category")
        genre = cleaned.get("genre")
        custom_cat = cleaned.get("custom_category")
        custom_gen = cleaned.get("custom_genre")
        location = cleaned.get("location")

        # Basic presence validation
        if not category:
            self.add_error("category", "Please select category")
        
        if not genre:
            self.add_error("genre", "Please select genre")

        if not location:
            self.add_error("location", "Location required")

        # Logic for "Others" Category & Uniqueness Check
        if category and category.name == "Others":
            if not custom_cat:
                self.add_error("custom_category", "Please enter a custom category")
            else:
                # Normalize (Trim space and capitalize like 'Fiction')
                normalized_cat = custom_cat.strip().title()
                # Check if this already exists in the database
                if Category.objects.filter(name__iexact=normalized_cat).exclude(name="Others").exists():
                    self.add_error("custom_category", f"'{normalized_cat}' already exists in the list. Please select it from the dropdown.")

        # Logic for "Others" Genre & Uniqueness Check
        if genre and genre.name == "Others":
            if not custom_gen:
                self.add_error("custom_genre", "Please enter a custom genre")
            else:
                # Normalize
                normalized_gen = custom_gen.strip().title()
                # Check existence
                if Genre.objects.filter(name__iexact=normalized_gen).exclude(name="Others").exists():
                    self.add_error("custom_genre", f"'{normalized_gen}' already exists. Please select it from the dropdown.")

        return cleaned