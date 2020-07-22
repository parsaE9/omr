from django import forms

class StatForm(forms.Form):
    post = forms.CharField()