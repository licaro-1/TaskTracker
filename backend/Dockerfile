FROM python:3.11-slim


WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --upgrade pip --no-cache-dir

RUN pip install -r ./requirements.txt --no-cache-dir

COPY . .

RUN chmod a+x docker/*.sh