FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py /app/
COPY push/* /app/push/

ENV TOKEN_KEY_FILE_NAME= DEVICE_TOKEN= TOKEN_KEY_FILE_NAME=
ENV LOG_LEVEL=INFO BARK_GROUP=短信 ENDPOINT=http://192.168.0.1


CMD ["python", "main.py"]