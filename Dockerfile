FROM python:3.10.9
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# 変数設定
ARG WORK_DIR=DjangoAutomaticallyApp
ARG USERNAME=django
ARG USER_UID=1000
ARG USER_GID=1000

# uwsgiのパスを通す
ENV PATH "$PATH:/home/$USERNAME/.local/bin"

# ユーザーを新規作成
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME
USER $USERNAME

# ワークスペースを作成
RUN mkdir /home/$USERNAME/$WORK_DIR
WORKDIR /home/$USERNAME/$WORK_DIR
COPY . /home/$USERNAME/$WORK_DIR

# pipライブラリをインストール&パーミッションを変更
RUN pip install --upgrade pip \
    && sudo chown -R $USERNAME:$USERNAME /home/$USERNAME/$WORK_DIR\
    && pip install -r /home/$USERNAME/$WORK_DIR/requirements.txt