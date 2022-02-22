FROM python:3.8

COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN apt update && apt install -qy default-libmysqlclient-dev gcc
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . /app

CMD [ "sh", "docker-entry.sh" ]