# 1時間くらいかかりますので気長に待ちましょう

FROM arm32v7/python:3.9.15-bullseye

RUN apt-get update && apt-get install -y sudo wget vim llvm
RUN pip install --upgrade pip wheel setuptools
RUN pip install numpy numba