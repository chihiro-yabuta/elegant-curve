FROM arm32v7/python:3.9.15-bullseye

RUN pip install --upgrade pip wheel setuptools
RUN pip install numpy