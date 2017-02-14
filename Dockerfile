FROM python:3.5.2

RUN mkdir -p /home/sites/app
WORKDIR /home/sites/app

COPY ./requirements.txt /home/sites/app/requirements.txt
RUN pip3 install -r requirements.txt

CMD [ "python", "./main.py"]
