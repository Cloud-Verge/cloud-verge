FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /protos/
WORKDIR /app

ADD ./balancer/ /app/
ADD ./protos/ /protos/

RUN apt update -y
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir /app/protos/
RUN python -m grpc_tools.protoc -I/protos --python_out=/app/protos --pyi_out=/app/protos --grpc_python_out=/app/protos /protos/balancer.proto
RUN python -m grpc_tools.protoc -I/protos --python_out=/app/protos --pyi_out=/app/protos --grpc_python_out=/app/protos /protos/posts.proto

ENTRYPOINT ["python", "main.py"]
