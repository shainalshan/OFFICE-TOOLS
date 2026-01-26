from django import forms
from .models import Document, Folder

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'folder']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 20 * 1024 * 1024: # 20MB
                raise forms.ValidationError("File size must be under 20MB.")
        return file

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent']
