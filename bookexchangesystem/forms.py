# from django import forms
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib.auth.models import User


# class LoginForm(AuthenticationForm):
#     username = forms.CharField(
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Username',
#             'class': 'login-input'
#         })
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             'placeholder': 'Password',
#             'class': 'login-input'
#         })
#     )

# class SignUpForm(AuthenticationForm):
#     username = forms.CharField(
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Username',
#             'class': 'signup-input'
#         })
#     )
#     email = forms.EmailField(
#         widget=forms.EmailInput(attrs={
#             'placeholder': 'Email',
#             'class': 'signup-input'
#         })
#     )
#     password1 = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             'placeholder': 'Password',
#             'class': 'signup-input'
#         })
#     )
#     password2 = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             'placeholder': 'Confirm Password',
#             'class': 'signup-input'
#         })
#     )