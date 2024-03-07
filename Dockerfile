FROM python:3.8-slim

ENV APP_HOME /app
ENV DATA_DIR /data

WORKDIR $APP_HOME

COPY src/ .

RUN pip install --user numpy matplotlib pandas scikit-learn scipy tqdm japanize_matplotlib
