from django import forms

class SubmitForm(forms.Form):
	text = forms.CharField(widget=forms.widgets.Textarea)

class WithdrawForm(forms.Form):
	address = forms.CharField()
