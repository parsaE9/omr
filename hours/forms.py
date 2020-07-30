from django import forms


class ChartDateForm(forms.Form):
    source = forms.DateField()
    end = forms.DateField()
