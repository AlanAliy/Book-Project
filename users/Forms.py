
from users.models import User
from django import forms

class RegisterForm(forms.ModelForm):

    username = forms.CharField(error_messages={"required": "Username is required",
                                               "min_length":"Username must be at least 5 characters",
                                               "max_length":"Username can not be more than 50 characters"},
                                               min_length=5, max_length=50)
    
    password = forms.CharField(error_messages={"required": "Username is required",
                                               "min_length": "Password must be at least 8 characters",
                                               "max_length": "Password can not be more than 150 characters"},
                                                min_length=8, max_length=150)
    
    email = forms.EmailField(error_messages={"required": "Email is required",
                                            "max_length": "Email must be shorter than 320 characters",
                                            "invalid": "email is invalid"},
                                             max_length=320)
    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        special_count=0
        digit_count=0
        for char in password:
            if char.isdigit():
                digit_count += 1
            elif not char.isdigit() and not char.isalpha() and char != ' ':
                    special_count += 1
        if special_count == 0 or digit_count == 0:
            raise forms.ValidationError("Password must contain a number and a special character")
        return password
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    

