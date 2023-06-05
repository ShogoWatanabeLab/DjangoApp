from django import forms


#  DjangoViews自動生成ツールフォーム
class XLSXForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    xlsx_file = forms.FileField(label="XLSXファイルを選択")
