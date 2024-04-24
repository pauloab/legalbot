from django import forms


class DocumentForm(forms.Form):
    file = forms.FileField(required=True, label="Reglamento en formato PDF")
