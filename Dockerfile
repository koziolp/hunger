
# syntax=docker/dockerfile:1

FROM python:3.7-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "application.py"]
EXPOSE 5000