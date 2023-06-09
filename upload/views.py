# imported module
import os, re, shutil, zipfile
import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader

from django.http import HttpResponse
from django.utils import timezone
from django.http import FileResponse
from django.views.generic import FormView
from project.settings import BASE_DIR
from .forms import *


# 動画アップロード申込画面
class UploadPage(FormView):
    template_name = "input.html"
    form_class = XLSXForm

    def form_valid(self, form):
        # Set file path and Load file
        xlsx_file = pd.ExcelFile(form.cleaned_data["xlsx_file"])
        all_sheet_names = xlsx_file.sheet_names

        env = Environment(loader=FileSystemLoader(f"{BASE_DIR}/tpl", encoding="utf8"))
        model_tpl = env.get_template("model.py-tpl")
        admin_tpl = env.get_template("admin.py-tpl")

        # Create parent dirs
        today = timezone.now().strftime("%Y%m%d")
        FULL_OUTPUT_DIR_PATH = f"{BASE_DIR}/{today}_output"
        self.create_dirs(FULL_OUTPUT_DIR_PATH)

        df = pd.read_excel(xlsx_file, sheet_name=all_sheet_names)
        db_table_info = self.get_db_table_info(df.get("テーブル一覧"))

        dirs_set = self.get_dirs_set(db_table_info)

        for dir_name in list(dirs_set):
            # Create child dirs
            self.create_dirs(f"{FULL_OUTPUT_DIR_PATH}/{dir_name}")

            # Create params
            table_info_list = []
            for key in db_table_info.keys():
                if re.match(dir_name, key):
                    table_info = db_table_info[key]
                    db_field_sheet = df.get(db_table_info[key]["logical_name"])
                    table_info["field_list"] = self.get_fields(db_field_sheet)
                    table_info_list.append(table_info)

            table_info_params = {
                "table_list": table_info_list,
                "dirs_list": list(dirs_set),
            }

            # model
            model_rendered = model_tpl.render(table_info_params)
            self.save_file(
                f"{FULL_OUTPUT_DIR_PATH}/{dir_name}/models.py", model_rendered
            )

            # admin
            admin_rendered = admin_tpl.render(table_info_params)
            self.save_file(
                f"{FULL_OUTPUT_DIR_PATH}/{dir_name}/admin.py", admin_rendered
            )

        # Zip
        response = HttpResponse(content_type="application/zip")
        with zipfile.ZipFile(response, "w") as zip:
            for file_path in self.get_dir_path(FULL_OUTPUT_DIR_PATH):
                # ZIPパスからhome/~/toolまでのパスを削除
                zip_path = file_path.replace(f"{FULL_OUTPUT_DIR_PATH}/", "")

                # ZIPフォルダに書き込む
                zip.write(file_path, zip_path)
            zip.close()

        # Download
        response["Content-Disposition"] = 'attachment; filename="output.zip"'

        # Remove output dir
        shutil.rmtree(FULL_OUTPUT_DIR_PATH)

        return response

    def create_dirs(self, path):
        os.makedirs(path, exist_ok=True)

    def get_db_table_info(self, df):
        # Preprocessing
        TABLE_COLUMNS = [
            "id",
            "logical_name",
            "dirs__table_name",
            "class_name",
            "super_class",
            "verbose_name",
            "verbose_name_plural",
            "memo",
        ]

        df_main = df[5:].replace(np.nan, "", regex=True)
        df_main.columns = TABLE_COLUMNS

        # Cerate dictionary
        dict_main = {row[2]: row.to_dict() for index, row in df_main.iterrows()}

        return dict_main

    def get_dirs_set(self, dirs__table_dict):
        dirs_set = set(
            [
                self.extract_dirs_name(value["dirs__table_name"])
                for value in dirs__table_dict.values()
            ]
        )

        return sorted(dirs_set)

    def get_fields(self, df):
        # Preprocessing
        FIELD_COLUMNS = [
            "id",
            "domain_name",
            "is_pk",
            "is_uk",
            "comment",
            "field_name",
            "data_type",
            "verbose_name",
            "on_delete",
            "blank",
            "null",
            "max_length",
            "help_text",
            "auto_now",
            "auto_now_add",
            "upload_to",
            "default",
            "foreign_class",
            "memo",
        ]

        df_main = (
            df[13:]
            .replace(np.nan, "", regex=True)
            .replace("True", True, regex=True)
            .replace("False", False, regex=True)
        )
        df_main.columns = FIELD_COLUMNS

        # Cerate list
        list_main = [row.to_dict() for index, row in df_main.iterrows()]

        return list_main

    def extract_dirs_name(self, str):
        return str[: re.search(r"__", str).start()]

    def save_file(self, path, file):
        with open(path, "w") as f:
            f.write(file)

    def get_dir_path(self, root):
        for root, dirs, files in os.walk(root):
            for file in files:
                yield os.path.join(root, file)
