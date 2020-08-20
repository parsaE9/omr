from django import forms
import xlrd

class ChartDateForm(forms.Form):
    source = forms.DateField()
    end = forms.DateField()
