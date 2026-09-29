# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# requirements.txt is UTF-16 + CRLF in the repo; pip needs UTF-8 with LF.
COPY requirements.txt .
RUN iconv -f UTF-16 -t UTF-8 requirements.txt | tr -d '\r' > utf8-requirements.txt \
    && pip install --no-cache-dir -r utf8-requirements.txt gunicorn \
    && rm utf8-requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
