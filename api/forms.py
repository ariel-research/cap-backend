from django import forms
from django.contrib.auth.models import User
from .models import Student
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password

class RegitrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1']
        extra_kwargs = {'password2': {'write_only': True, 'required': True}}
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1, self.instance)
        except forms.ValidationError as error:
            self.add_error('password1', error)
        return password1
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username= self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.password1 = self.cleaned_data['password1']
        user.password2 = self.cleaned_data['password2']
        if commit:
            user.save()
        return user
    
class StudentForm(forms.ModelForm):
    
    class Meta:
        model = Student
        fields = ['student_id','program','amount_elective']