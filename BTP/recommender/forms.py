from django.forms import ModelForm, Textarea
from recommender.models import Review,Product

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        labels = {'review_text': ('Comment'),}
        widgets = {
            'review_text': Textarea(attrs={'cols': 40, 'rows': 15})
        }
        
class PollsForm(ModelForm):
	class Meta:
		model=Product
		fields=[
		'name'
		]
        labels = {'name' : ('Product')}
        
from django import forms

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Upload an Image',
    )
