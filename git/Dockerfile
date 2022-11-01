FROM python:3.9.15

RUN pip install --upgrade pip wheel setuptools

COPY git/requirements.txt requirements.txt
RUN pip install -r requirements.txt
