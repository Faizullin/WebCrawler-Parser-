from .models import  SearchedLink
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class  SearchedLinkForm(forms.ModelForm):
    article_news_block = forms.CharField(label='Блок', widget=forms.TextInput(attrs={'class': 'form-input','value':"article_container" }))
    article_news_title = forms.CharField(label='Название', widget=forms.TextInput(attrs={'class': 'form-input ','value':"title_article_bl" }))
    article_news_body = forms.CharField(label='Контент', widget=forms.TextInput(attrs={'class': 'form-input','value':"body_article_bl" }))
    url = forms.URLField(widget=forms.URLInput(attrs={'type': 'URL','id':"id_search_link",'class': 'myrounded inputText','placeholder': 'https://'}))
    #error_body=forms.CharField()
    class Meta:
        model =  SearchedLink
        fields="__all__"#["urlint"]
        exclude = ['error_body','creator_id']

class RegisterUserForm(UserCreationForm):

    username=forms.CharField(label = 'Логин',widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label = 'Email',widget = forms.EmailInput(attrs={'class':'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    class Meta:
        model = User
        fields=('username','email',"password1","password2")
class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input inputText'}))
    #email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input inputText'}))
    class Meta:
        model = User
        fields=('username',"password")


class DownloadForm(forms.Form):
    file_number_choices = (('10','< 10'),('50','< 50'),('100','< 100'))
    file_type_choices=(('xlsx','Excell'),('doc','Docx'),('txt',"Txt"))
    file_number= forms.CharField(label='Pages to be crawled' ,widget=forms.RadioSelect(attrs={'class':"form-check-input"},choices=file_number_choices))
    file_type= forms.CharField(label='Save in', widget=forms.RadioSelect(attrs={'class':"form-check-input"},choices=file_type_choices))
