from django import forms
from contest.models import Submission

class SubmitForm(forms.ModelForm):
	class Meta:
		model = Submission
		fields = [ 'text' ]

class WithdrawForm(forms.Form):
	address = forms.CharField()
