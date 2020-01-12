FROM python:3.7

RUN mkdir /dependencies
WORKDIR /dependencies
COPY requirements.txt /dependencies/
RUN pip3 install -r requirements.txt
