from django import forms


class DocumentForm(forms.Form):
    title = forms.CharField(max_length=200, required=False, label="Título")
    file = forms.FileField(required=True, label="Reglamento en formato PDF")
