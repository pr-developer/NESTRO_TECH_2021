FROM python:3.8.5-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGOHOSTS dn.bitc.ru

RUN apt-get update && apt-get upgrade -y

RUN pip install --upgrade pip

COPY ./reqmin.txt .
RUN pip install -r reqmin.txt

COPY . .

RUN pip install gunicorn
WORKDIR /usr/src/app/monstability
