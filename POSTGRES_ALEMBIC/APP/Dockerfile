FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libpq-dev \
    gcc \
    && apt-get clean
RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY main.py /app/

WORKDIR /app

COPY entrypoint.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]