FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install --upgrade setuptools wheel
RUN pip install -r requirements.txt

COPY main_app .

ENV FLASK_APP=run.py
ENV FLASK_ENV=development

EXPOSE 5000

ENTRYPOINT ["python", "run.py"]