FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir /tic_tac_toe
WORKDIR /tic_tac_toe
ADD requirements.txt /tic_tac_toe/
RUN pip install -r requirements.txt
ADD . /tic_tac_toe/