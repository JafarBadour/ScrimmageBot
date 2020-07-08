FROM ubuntu:16.04
FROM python:3.7
RUN apt-get update -y
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY ./ /app/

CMD ["python", "app.py"]