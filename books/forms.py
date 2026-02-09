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
        "placeholder":"Price (optional)"
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


        # Inject "Others" manually
        # self.fields["category"].choices = (
        #     list(self.fields["category"].choices) + [("other", "Others")]
        # )

        # self.fields["genre"].choices = (
        #     list(self.fields["genre"].choices) + [("other", "Others")]
        # )

        # Condition placeholder
        self.fields["condition"].choices = [("", "Condition")] + list(
            self.fields["condition"].choices
        )

    # =====================
    # Validation
    # =====================

    def clean(self):
        cleaned = super().clean()

        if not cleaned.get("category"):
            self.add_error("category", "Please select category")

        if not cleaned.get("genre"):
            self.add_error("genre", "Please select genre")

        if cleaned.get("category") == "other" and not cleaned.get("custom_category"):
            self.add_error("custom_category", "Please enter category")

        if cleaned.get("genre") == "other" and not cleaned.get("custom_genre"):
            self.add_error("custom_genre", "Please enter genre")

        if not cleaned.get("location"):
            self.add_error("location", "Location required")

        return cleaned

# class BookEditForm(forms.ModelForm):
#     custom_category = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={
#             "class": "form-control",
#             "placeholder": "Enter category"
#         })
#     )

#     custom_genre = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={
#             "class": "form-control",
#             "placeholder": "Enter genre"
#         })
#     )

#     location = forms.CharField(
#         widget=forms.TextInput(attrs={
#             "class": "form-control",
#             "placeholder": "Your City"
#         })
#     )

#     price = forms.DecimalField(
#     required=False,
#     widget=forms.NumberInput(attrs={
#         "class":"form-control",
#         "placeholder":"Price (optional)"
#     })
#     )


#     class Meta:
#         model = Book
#         fields = [
#             "title", "author", "description", "isbn",
#             "category", "genre", "custom_category", "custom_genre",
#             "language", "condition", "location", "cover_image", "price"
#         ]

#         widgets = {
#             "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Book title"}),
#             "author": forms.TextInput(attrs={"class": "form-control", "placeholder": "Author"}),
#             "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Description"}),
#             "isbn": forms.TextInput(attrs={"class": "form-control", "placeholder": "ISBN"}),
#             "language": forms.TextInput(attrs={"class": "form-control", "placeholder": "Language"}),
#             "cover_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
#             "category": forms.Select(attrs={"class": "form-control placeholder-select", "id": "category"}),
#             "genre": forms.Select(attrs={"class": "form-control placeholder-select", "id": "genre"}),
#             "condition": forms.Select(attrs={"class": "form-control placeholder-select"}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Only first 10 records
#         self.fields["category"].queryset = Category.objects.all()
#         self.fields["genre"].queryset = Genre.objects.all()

#         self.fields["category"].queryset = Category.objects.annotate(
#             is_other=Case(
#                 When(name="Others", then=Value(1)),
#                 default=Value(0),
#                 output_field=IntegerField(),
#             )
#         ).order_by("is_other", "name")

#         self.fields["genre"].queryset = Genre.objects.annotate(
#             is_other=Case(
#                 When(name="Others", then=Value(1)),
#                 default=Value(0),
#                 output_field=IntegerField(),
#             )
#         ).order_by("is_other", "name")

#         # Placeholder
#         self.fields["category"].choices = [("", "Category")] + list(self.fields["category"].choices)
#         self.fields["genre"].choices = [("", "Genre")] + list(self.fields["genre"].choices)


#         # Inject "Others" manually
#         # self.fields["category"].choices = (
#         #     list(self.fields["category"].choices) + [("other", "Others")]
#         # )

#         # self.fields["genre"].choices = (
#         #     list(self.fields["genre"].choices) + [("other", "Others")]
#         # )

#         # Condition placeholder
#         self.fields["condition"].choices = [("", "Condition")] + list(
#             self.fields["condition"].choices
#         )

#     # =====================
#     # Validation
#     # =====================

#     def clean(self):
#         cleaned = super().clean()

#         if not cleaned.get("category"):
#             self.add_error("category", "Please select category")

#         if not cleaned.get("genre"):
#             self.add_error("genre", "Please select genre")

#         if cleaned.get("category") == "other" and not cleaned.get("custom_category"):
#             self.add_error("custom_category", "Please enter category")

#         if cleaned.get("genre") == "other" and not cleaned.get("custom_genre"):
#             self.add_error("custom_genre", "Please enter genre")

#         if not cleaned.get("location"):
#             self.add_error("location", "Location required")

#         return cleaned
