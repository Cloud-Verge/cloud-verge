FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
ADD . /app/

WORKDIR /app
ADD requirements.txt requirements.txt

RUN apt update -y
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn", "--host", "*", "--port", "5000", "main:app"]