import os

from django import forms


#  DjangoViews自動生成ツールフォーム
class XLSXForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    xlsx_file = forms.FileField(label="XLSXファイルを選択")

    def clean_xlsx_file(self):
        xlsx_file = self.cleaned_data["xlsx_file"]
        extension = os.path.splitext(xlsx_file.name)[1]
        if extension.lower() != ".xlsx":
            raise forms.ValidationError("XLSXファイルを選択してください")
        return xlsx_file
