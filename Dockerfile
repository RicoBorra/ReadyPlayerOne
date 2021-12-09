FROM python:3.9.7-alpine
ADD . /readyplayerone
WORKDIR /readyplayerone
RUN pip install -r requirements.txt
RUN pip install gunicorn
