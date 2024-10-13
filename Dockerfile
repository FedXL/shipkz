FROM python:3.12-slim
WORKDIR /app
COPY req.txt /app/
RUN pip install -r req.txt
COPY . /app/
