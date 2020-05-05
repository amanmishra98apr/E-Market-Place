from django import forms


class NewUserForm(forms.Form):
    username=forms.CharField(label='username',max_length=100)
    email=forms.EmailField(label='email')
    password=forms.CharField(label='password',max_length=100)
    mobile=forms.IntegerField(label='mobile')

class LoginUserForm(forms.Form):
    email=forms.EmailField(label='email')
    password=forms.CharField(label='password')

class OneTimePasswordForm(forms.Form):
    otp=forms.CharField(label='otp',widget=forms.Textarea(attrs={'cols':35,'rows':1}))
