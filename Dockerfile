FROM python:3.12

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt app/requirements.txt
RUN pip3 install -r app/requirements.txt

COPY /app/. /app