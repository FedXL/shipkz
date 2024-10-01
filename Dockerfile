FROM python:3.12-alpine
WORKDIR /app
COPY req.txt /app/
RUN pip install --no-cache-dir -r req.txt
COPY . /app/
